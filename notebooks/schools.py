import pandas as pd
import re
from fuzzywuzzy import fuzz
from itertools import chain
from scipy import stats
import random
from ksdisc import ks_disc_2sample
import numpy as np

"""
Constants for subsets of columns
"""
SCHOOL_BASIC = [
 'dbn',
 'school_name',
 'year',
 'total_enrollment',
 'district',
 'boro',
 'boro_name'
]

DEMO_GROUPS = [
 'female',
 'female_1',
 'male',
 'male_1',
 'asian',
 'asian_1',
 'black',
 'black_1',
 'hispanic',
 'hispanic_1',
 'multiple_race_categories',
 'multiple_race_categories_1',
 'white',
 'white_1',
 'students_with_disabilities',
 'students_with_disabilities_1',
 'english_language_learners',
 'english_language_learners_1',
 'poverty',
 'poverty_1',
 'non_white',
 'non_white_1',
 'black_hispanic',
 'black_hispanic_1',
 'white_asian',
 'white_asian_1',
 'non_white_asian',
 'non_white_asian_1'
]


def load_charter_math():
    url = "https://data.cityofnewyork.us/resource/3xsw-bpuy.csv?$limit=10000000"
    df = pd.read_csv(url)
    return df



def load_demo_open_data():
    demo_url = "https://data.cityofnewyork.us/resource/nie4-bv6q.csv?$limit=10000000"
    df = pd.read_csv(demo_url)
    return df


def load_demographics():
    """
    Loads the NYC school-level demographic data from the
    open data portal and create a dataframe., ascending=False
    Adds new columns to the dataframe:
         short_name: the best guess at the nuload_ELAtestmerical name of the school (e.g. PS 9)
                     or "" if none exists
           district: the school district number [1..32, 75, 79, 84]
               boro: borough code string ["M","B","X","Q","R"]
          boro_name: string of the full borough name
               year: the academic year as an integer representing the calendar
                     year in the fall of the school year
        white_asian: combined number of white and asian students
          non_white: total number of non white students
    non_white_asian: total number of non white or asian students
     black_hispanic: total number of black and hispanic students
    return the dataframe
    """
    # load the school demo data from the open api server
    df = load_demo_open_data()


    boros = {"M":"Manhattan", "K": "Brooklyn", "X":"Bronx", "R":"Staten Island", "Q":"Queens"}

    # figure out what grades they teach
    df["pk"] = df["grade_3k_pk_half_day_full"] > 0
    df["elementary"] = df["grade_2"] > 0
    df["middle"] = df["grade_7"] > 0
    df["hs"] = df["grade_10"] > 0

    # parse data from dbn
    df["year"] = df.year.apply(lambda year: int(year[:4]))
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
    df["non_white_1"] = df.non_white / df.total_enrollment

    df["black_hispanic"] = df.black + df.hispanic
    df["black_hispanic_1"] = df.black_hispanic / df.total_enrollment

    df["white_asian"] = df.white + df.asian
    df["white_asian_1"] = df.white_asian / df.total_enrollment

    df["non_white_asian"] = df.total_enrollment - df.white_asian
    df["non_white_asian_1"] = df.non_white_asian / df.total_enrollment


    pct_cols = [col for col in df.columns if col.endswith("_1") and col != "grade_1"]

    df = df.apply(lambda x: pct_to_float(x, pct_cols), axis=1)
    for col in pct_cols:
        df[col] = pd.to_numeric(df[col])

    return df


def pct_to_float(row, cols):
    """
    Cleans data that is expected to be a percentage expressed
    as a float. If the data is a string ending in a % sign, it's
    converted to a float. If the sample is too small ("Below 5%"),
    return .04, if the sample is too high, ("Above 95%") return .96
    @row the row of the DataFrame
    @cols the column names that should be converted to percents between 0 and 1
    @return the row with the coerced float values
    """
    for col in cols:
        try:
            float(row[col])
            continue
        except:
            pass

        if "Below" in row[col]:
            row[col] = .04
        elif "Above" in row[col]:
            row[col] = .96
        else:
            pct = str(row.poverty_1)[:-1]
            row[col] = float(pct) / 100
    return row

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
    latest = t.year.max()

    # first lookup by number
    t = t.query(f"short_name == '{qry.upper()}' and year=={latest}")
    if len(t) > 0:
        return t

    # fuzzy search
    t = df.copy(deep=False)

    t["match"] = t.clean_name.apply(lambda sn: fuzz.token_set_ratio(qry, sn))
    t = t.query(f"match > 80 and year=={latest}")
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

    districts = df.groupby(["district", "year"]).agg(demo_agg).reset_index()
    districts = districts.rename(columns={"dbn":"num_schools"})
    del demo_agg["dbn"]

    # add a new col that combines blackand hispanic
    # this might not be right, if we are double counting students who are black and hispanic
    districts["black_hispanic"] = districts.black + districts.hispanic

    for demo in demo_agg:
        districts[demo + "_pct"] = districts[demo] / districts.total_enrollment

    districts.sort_values(by="district")
    return districts




def clean_test_data_categories(df):
    # normalize the categories that will become columns
    del df["school_name"]

    df["category"] = df["category"].apply(lambda cat: cat.lower())
    df.loc[df['category'] == "all students", 'category'] = "all"
    df.loc[df['category'] == "all students", 'category'] = "all"
    df.loc[df['category'] == "never ell", 'category'] = "never_ell"
    df.loc[df['category'] == "ever ell", 'category'] = "ever_ell"
    df.loc[df['category'] == "current ell", 'category'] = "current_ell"
    df.loc[df['category'] == "swd", 'category'] = "swd"
    df.loc[df['category'] == "not swd", 'category'] = "not_swd"
    df.loc[df['category'] == "swd", 'category'] = "swd"
    df.loc[df['category'] == "econ disadv", 'category'] = "econ_disadv"
    df.loc[df['category'] == "not econ disadv", 'category'] = "not_econ_disadv"
    df.loc[df['grade'] == "all grades", 'grade'] = "all"

    df.loc[df['grade'] == "All Grades", 'grade'] = "all"
    return df

def make_test_cols(test_df):
    """
    Takes a dataframe of ela or math test data and makes
    column headers baed on the unique categories for `grade`
    and `category.` `grade` indicates the numeric grade level of students (3-8)
    and `category` is the demographic group of the test takers (e.g. SWD, Asian)
    return a list of tuples of every (category, grade) combination (e.g. ('black', 8))
    """
    grades = test_df.grade.unique()
    cats = test_df.category.unique()
    combos = [[(cat, grade) for grade in grades] for cat in cats]
    combos = list(chain.from_iterable(combos))
    return combos


def load_math_tests():
    """
    Loads the NYC Math test data from the
    open data portal and create a dataframe.
    return the dataframe
    """
    # load the school ELA test data from the open api server
    MATH_url = "https://data.cityofnewyork.us/resource/m27t-ht3h.csv?$limit=10000000"
    df = pd.read_csv(MATH_url)
    df = clean_test_data_categories(df)

    return df


def load_ela_tests():
    """
    Loads the NYC ELA test data from the
    open data portal and create a dataframe.
    """
    # load the school ELA test data from the open api server
    ELA_url = "https://data.cityofnewyork.us/resource/qkpp-pbi8.csv?$limit=10000000"

    df = pd.read_csv(ELA_url)
    df = clean_test_data_categories(df)

    return df

def rows_to_cols(cat, grade, test_df, prefix="math"):
    """
        get the test result rows for one (category, grade)
        combination and make them columns in a new dataframe
    """

    # all of the cols that contain test-related data
    test_cols = ['number_tested',
        'mean_scale_score',
        'level_1',
        'level_1_1',
        'level_2',
        'level_2_1',
        'level_3',
        'level_3_1',
        'level_4',
        'level_4_1',
        'level_3_4',
        'level_3_4_1']
    temp_df = test_df.query(f"category == '{cat}' and grade == '{grade}'")
    new_cols = [f"{prefix}_{cat}_grade_{grade}_{col}" for col in test_cols]
    rename = dict(zip(test_cols, new_cols))
    temp_df = temp_df.rename(columns = rename)
    temp_df = temp_df.drop(["grade", "category"], axis=1)
    temp_df.set_index(["dbn", "year"])
    return temp_df

def combine_test_data(df, test_df, test_type="math"):
    """
    Combine test result data with the schools dataframe to make a wide
    data set where row data from test results (grade and demographic category)
    become columns in the new combined dataframe
    - df: the schools DataFrame
    - test_df: the DataFrame with the test results
    - test_type: either math or ela
    """

    # cat all combinations of test takers
    combos = make_test_cols(test_df)

    # get an array of df for each combo
    grade_cat_results = [rows_to_cols(cat, grade, test_df, test_type) for cat, grade in combos]


    # merge the category dataframes in with the school data
    combined = df.copy()
    for t in grade_cat_results:
        combined = combined.merge(t,on=["dbn", "year"], how="left")

    return combined

###################################################################################################

def segregation_test(demo_df):
    """
    Here we perform the chi-square test to see the segregation of the
    ethnic populations for each school...
    Let us recall that we want to compare the distribution at the level
    of district with the distribution at the level of school.
    We have four cathegories asian, black, white and hispanic;
    each school has its own observed frequencies f_obs and we are going to
    compare with the expected frequencies f_exp from the distribution at the district level...
    """

    # The probabilities from the district level...
    N_total    = demo_df.groupby(["district","year"]).agg('sum')
    p_asian    = N_total["asian"]/N_total["total_enrollment"]
    p_white    = N_total["white"]/N_total["total_enrollment"]
    p_black    = N_total["black"]/N_total["total_enrollment"]
    p_hispanic = N_total["hispanic"]/N_total["total_enrollment"]
    p_multrace = N_total["multiple_race_categories"]/N_total["total_enrollment"]

    # Data at the level of school...
    N_school   = demo_df.groupby(["district","year","school_name"]).agg('sum')

    y_data = []
    d_data = []
    school_name_data = []
    chi2_pvalue_data = []
    chi2_value_data  = []
    KS_pvalue_data   = []
    for i in range(0, len(demo_df)):
        d = int(demo_df.loc[i,"district"])
        d_data.append(d)
        y = int(demo_df.loc[i,"year"])
        y_data.append(y)
        sch_name = demo_df.loc[i,"school_name"]
        school_name_data.append(sch_name)
        # This are the observed frequencies f_obs...by school in district "d" and for year "y"...
        x_asian    = N_school.loc[(d,y,sch_name),"asian"]
        x_white    = N_school.loc[(d,y,sch_name),"white"]
        x_black    = N_school.loc[(d,y,sch_name),"black"]
        x_hispanic = N_school.loc[(d,y,sch_name),"hispanic"]
        x_multrace = N_school.loc[(d,y,sch_name),"multiple_race_categories"]
        f_obs      = [x_asian, x_white, x_black, x_hispanic, x_multrace]
        # This are the expected frequencies f_exp...by school in district "d" and for year "y"...
        m_asian    = p_asian[(d,y)] * N_school.loc[(d,y,sch_name),"total_enrollment"]
        m_white    = p_white[(d,y)] * N_school.loc[(d,y,sch_name),"total_enrollment"]
        m_black    = p_black[(d,y)] * N_school.loc[(d,y,sch_name),"total_enrollment"]
        m_hispanic = p_hispanic[(d,y)] * N_school.loc[(d,y,sch_name),"total_enrollment"]
        m_multrace = p_multrace[(d,y)] * N_school.loc[(d,y,sch_name),"total_enrollment"]
        f_exp      = [m_asian, m_white, m_black, m_hispanic, m_multrace]
        # Chi_square statistic and p-value
        chi2 = stats.chisquare(f_obs,f_exp)
        chi2_value_data.append(chi2[0])
        chi2_pvalue_data.append(chi2[1])
        # Let us note that we can also compute also the KS test as follows from the above data
        sample1 = np.concatenate((np.ones(int(round(m_asian))), 2*np.ones(int(round(m_white))), 3*np.ones(int(round(m_black))),
                             4*np.ones(int(round(m_hispanic))), 5*np.ones(int(round(m_multrace)))))
        sample2 = np.concatenate((np.ones(int(x_asian)), 2*np.ones(int(x_white)), 3*np.ones(int(x_black)),
                             4*np.ones(int(x_hispanic)), 5*np.ones(int(x_multrace))))
        list1 = sample1.tolist()
        list2 = sample2.tolist()
        if (len(list1)==len(list2)):
            KS_pvalue = ks_disc_2sample( list1, list2 )
            KS_pvalue_data.append( KS_pvalue )
        elif (len(list1) > len(list2)):
            random_item_from_list = random.choice(list1)
            list1.remove(random_item_from_list)
            KS_pvalue = ks_disc_2sample( list1, list2 )
            KS_pvalue_data.append( KS_pvalue )
        elif (len(list1) < len(list2)):
            random_item_from_list = random. choice(list2)
            list2.remove(random_item_from_list)
            KS_pvalue = ks_disc_2sample( list1, list2 )
            KS_pvalue_data.append( KS_pvalue )

    # Since the script spent some time until finish, it is better to have the data in a .csv file
    # Below we construct that file...
    header_csv = " p_value_chi2test, chi2_value_chi2test, p_value_KStest      "
    Dls_modif_to_dat = np.column_stack( ( chi2_pvalue_data, chi2_value_data, KS_pvalue_data ) )
    np.savetxt( 'segregation_tests.csv',
	    Dls_modif_to_dat, delimiter=',', header= header_csv, fmt=['%18.12E','%18.12E','%18.12E'] )


    return (chi2_pvalue_data, chi2_value_data, KS_pvalue_data)



#demo_df["p_value_chi2test"]    = chi2_pvalue_data
#demo_df["chi2_value_chi2test"] = chi2_value_data
#demo_df["p_value_KStest"]      = KS_pvalue_data
