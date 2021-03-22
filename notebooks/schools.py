import pandas as pd
import re
from fuzzywuzzy import fuzz

def load_charter_math():
    url = "https://data.cityofnewyork.us/resource/3xsw-bpuy.csv?$limit=10000000"
    df = pd.read_csv(url)
    return df

def load_demographics():
    """
    Loads the NYC school-level demographic data from the
    open data portal and create a dataframe.
    Adds new columns to the dataframe:

         short_name: the best guess at the numerical name of the school (e.g. PS 9)
                     or "" if none exists

           district: the school district number [1..32, 75, 79, 84]
               boro: borough code string ["M","B","X","Q","R"]
          boro_name: string of the full borough name
                 ay: the academic year as an integer representing the calendar
                     year in the fall of the school year
        white_asian: combined number of white and asian students
          non_white: total number of non white students
    non_white_asian: total number of non white or asian students
     black_hispanic: total number of black and hispanic students

    return the dataframe
    """
    # load the school demo data from the open api server
    demo_url = "https://data.cityofnewyork.us/resource/nie4-bv6q.csv?$limit=10000000"
    boros = {"M":"Manhattan", "K": "Brooklyn", "X":"Bronx", "R":"Staten Island", "Q":"Queens"}
    df = pd.read_csv(demo_url)


    # figure out what grades they teach
    df["pk"] = df["grade_3k_pk_half_day_full"] > 0
    df["elementary"] = df["grade_1"] > 0
    df["middle"] = df["grade_7"] > 0
    df["hs"] = df["grade_10"] > 0

    # parse data from dbn
    df["ay"] = df.year.apply(lambda year: int(year[:4]))
    df["district"] = df.dbn.apply(lambda dbn: int(dbn[:2]))
    df["school_num"] = df.dbn.apply(lambda dbn: int(dbn[3:]))
    df["boro"] = df.dbn.apply(lambda dbn: dbn[2])
    df["boro_name"] = df.boro.apply(lambda x: boros[x])

    # make it easier to look up schools
    df["school_type"] = df.apply(school_type, axis=1)

    df["clean_name"] = df.apply(lambda row: clean_name(row.school_name), axis=1)

    df["short_name"] = df.apply(short_name, axis=1)

    # add a few demo groups
    df["non_white"] = df.total_enrollment - df.white
    df["black_hispanic"] = df.black + df.hispanic
    df["white_asian"] = df.white + df.asian
    df["non_white_asian"] = df.total_enrollment - df.white_asian

    return df


def school_type(school):
    """
        Any school that serves middle school kids
        is considered a middle school here.
    """

    if school["middle"]:
        return "MS"
    if school["elementary"]:
        return "PS"
    if school["hs"]:
        return "HS"
    return "NA"


def clean_name(sn):
    sn = sn.lower()
    sn = sn.strip()
    sn = sn.replace(".", "")
    clean = []
    for word in sn.split(" "):
        try:
            n = int(word)
            clean.append(str(n))
        except:
            clean.append(word)

    sn = " ".join(clean)

    p = re.compile(r"\b([m|p|i]s [0-9]*)")
    m = p.search(sn)
    if m:
        sn = sn.replace(m.group(0), "")
    return sn


def short_name(row):
    sn = row.school_name.upper()
    if "P.S." in sn or "P. S." in sn:
        return f"PS {row.school_num}"

    if "M.S." in sn or "M. S." in sn:
        return f"MS {row.school_num}"

    if "I. S." in sn or "I.S." in sn:
        return f"IS {row.school_num}"

    return f"{row.school_type} {row.school_num}"



def find_school(df, qry):
    t = df.copy(deep=False)
    latest = t.ay.max()

    # first lookup by number
    t = t.query(f"short_name == '{qry.upper()}' and ay=={latest}")
    if len(t) > 0:
        return t

    # fuzzy search
    t = df.copy(deep=False)

    t["match"] = t.clean_name.apply(lambda sn: fuzz.token_set_ratio(qry, sn))
    t = t.query(f"match > 80 and ay=={latest}")
    t = pd.DataFrame(t)
    # now sort the results based on the ratio match
    t["match"] = t.clean_name.apply(lambda sn: fuzz.ratio(qry, sn))
    t = t.sort_values(by=["match"], ascending=False)

    return t

def calc_districts(df):
    # calculate boro and district averages for each demo group


    # first get the sums
    demo_agg = {
        'total_enrollment': "sum",
        'black': "sum",
        'white': "sum",
        'asian': "sum",
        'hispanic': "sum",
        'multiple_race_categories': "sum",
        'students_with_disabilities': "sum",
        'english_language_learners': "sum",
        'poverty': "sum",
        "non_white": "sum",
        "black_hispanic": "sum",
        "white_asian": "sum",
        "non_white_asian": "sum",
        "dbn": "count"
    }

    districts = df.groupby(["district", "year", "ay"]).agg(demo_agg).reset_index()
    districts = districts.rename(columns={"dbn":"num_schools"})
    del demo_agg["dbn"]

    # add a new col that combines blackand hispanic
    # this might not be right, if we are double counting students who are black and hispanic
    districts["black_hispanic"] = districts.black + districts.hispanic

    for demo in demo_agg:
        districts[demo + "_pct"] = districts[demo] / districts.total_enrollment

    districts.sort_values(by="black_pct", ascending=False)
    return districts
