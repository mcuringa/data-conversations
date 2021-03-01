import pandas as pd


def load_demographics():
    """
    Loads the NYC school-level demographic data from the
    open data portal and create a dataframe.
    Adds new columns to the dataframe:

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
    demo_url = "https://data.cityofnewyork.us/resource/45j8-f6um.csv?$limit=10000000"
    boros = {"M":"Manhattan", "K": "Brooklyn", "X":"Bronx", "R":"Staten Island", "Q":"Queens"}
    df = pd.read_csv(demo_url)

    df["ay"] = df.year.apply(lambda year: int(year[:4]))

    df["district"] = df.dbn.apply(lambda dbn: int(dbn[:2]))
    df["boro"] = df.dbn.apply(lambda dbn: dbn[2])
    df["boro_name"] = df.boro.apply(lambda x: boros[x])

    df["non_white"] = df.total_enrollment - df.white
    df["black_hispanic"] = df.black + df.hispanic
    df["white_asian"] = df.white + df.asian
    df["non_white_asian"] = df.total_enrollment - df.white_asian

    return df

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
        "non_white_asian": "sum"
    }

    districts = df.groupby(["district", "year"]).agg(demo_agg).reset_index()

    # add a new col that combines blackand hispanic
    # this might not be right, if we are double counting students who are black and hispanic
    districts["black_hispanic"] = districts.black + districts.hispanic

    for demo in demo_agg:
        districts[demo + "_pct"] = districts[demo] / districts.total_enrollment

    districts.sort_values(by="black_pct", ascending=False)
    return districts
