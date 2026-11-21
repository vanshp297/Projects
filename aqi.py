"""
=====================================================================
  AQI GENERATOR & ANALYZER  -  Data Analytics Training Project
=====================================================================
Ek hi file me poora project. Run karne ke liye VS Code terminal me:

        python aqi_generator.py

Is file me 3 Python modules (aqi_calculator, data_manager,
analysis_tools) ke source code diye gaye hain. Program start hote hi
ye modules create hote hain aur `import` kiye jaate hain.

Mandatory parameters ka mapping:
  1. Dataset (50+ records)  -> data_manager.create_dataset()  (60 records, CSV)
  2. Data structures        -> list, tuple, set, dict, list & dict methods
  3. User-defined functions -> 25+ functions (har module me)
  4. NumPy                  -> analysis_tools.numpy_analysis()
  5. Pandas                 -> analysis_tools.pandas_analysis()
  6. Python modules         -> 3 modules (neeche) + import
  7. File handling          -> CSV read / write / append (data_manager)
  8. Project functionality  -> Add, Display, Search, Update, Delete, Summary
  9. Data analysis          -> analysis_tools.generate_insights()
 10. Output presentation    -> formatted terminal output
=====================================================================
"""

import sys
import types

# ---------------------------------------------------------------------
# MODULE 1 : aqi_calculator  (AQI nikalne ka logic - CPCB India formula)
# ---------------------------------------------------------------------
AQI_CALCULATOR_SRC = r'''
"""Module 1: AQI calculation logic (CPCB India breakpoints)."""

# ----- DATA STRUCTURE 1: TUPLE (fixed pollutant list) -----
POLLUTANTS = ("PM2.5", "PM10", "NO2", "SO2", "CO", "O3")

# ----- DATA STRUCTURE 2: DICTIONARY of LISTS of TUPLES -----
# (conc_low, conc_high, index_low, index_high)
BREAKPOINTS = {
    "PM2.5": [(0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200),
              (91, 120, 201, 300), (121, 250, 301, 400), (251, 500, 401, 500)],
    "PM10":  [(0, 50, 0, 50), (51, 100, 51, 100), (101, 250, 101, 200),
              (251, 350, 201, 300), (351, 430, 301, 400), (431, 800, 401, 500)],
    "NO2":   [(0, 40, 0, 50), (41, 80, 51, 100), (81, 180, 101, 200),
              (181, 280, 201, 300), (281, 400, 301, 400), (401, 800, 401, 500)],
    "SO2":   [(0, 40, 0, 50), (41, 80, 51, 100), (81, 380, 101, 200),
              (381, 800, 201, 300), (801, 1600, 301, 400), (1601, 2400, 401, 500)],
    "CO":    [(0, 1, 0, 50), (1.1, 2, 51, 100), (2.1, 10, 101, 200),
              (10.1, 17, 201, 300), (17.1, 34, 301, 400), (34.1, 50, 401, 500)],
    "O3":    [(0, 50, 0, 50), (51, 100, 51, 100), (101, 168, 101, 200),
              (169, 208, 201, 300), (209, 748, 301, 400), (749, 1000, 401, 500)],
}

# ----- DATA STRUCTURE 3: LIST of TUPLES (AQI upper limit, category) -----
CATEGORIES = [(50, "Good"), (100, "Satisfactory"), (200, "Moderate"),
              (300, "Poor"), (400, "Very Poor"), (500, "Severe")]

# ----- DATA STRUCTURE 4: DICTIONARY (health advice) -----
HEALTH_ADVICE = {
    "Good": "Minimal impact. Enjoy outdoor activities.",
    "Satisfactory": "Sensitive people may feel minor breathing discomfort.",
    "Moderate": "People with lung/heart disease, children and elderly should limit outdoor effort.",
    "Poor": "Breathing discomfort on prolonged exposure. Wear a mask outdoors.",
    "Very Poor": "Respiratory illness on prolonged exposure. Avoid outdoor activity.",
    "Severe": "Serious health impact. Stay indoors and use air purifiers.",
}


def is_missing(value):
    """Check karta hai ki value missing (None / NaN) hai ya nahi."""
    return value is None or value != value


def calculate_sub_index(pollutant, concentration):
    """Ek pollutant ka sub-index nikalta hai (linear interpolation)."""
    if is_missing(concentration):
        return None
    for c_low, c_high, i_low, i_high in BREAKPOINTS[pollutant]:
        if concentration <= c_high:
            value = (i_high - i_low) / (c_high - c_low) * (concentration - c_low) + i_low
            return int(round(max(value, 0)))
    return 500


def get_category(aqi):
    """AQI value se category batata hai."""
    for upper_limit, name in CATEGORIES:
        if aqi <= upper_limit:
            return name
    return "Severe"


def calculate_aqi(readings):
    """
    readings : dict {pollutant: value}
    Return   : (aqi, dominant_pollutant, category)
    CPCB rule: kam se kam 3 pollutants ho aur unme PM2.5 ya PM10 zaroor ho.
    """
    sub_indices = {}
    for pollutant in POLLUTANTS:
        sub = calculate_sub_index(pollutant, readings.get(pollutant))
        if sub is not None:
            sub_indices[pollutant] = sub

    has_pm = "PM2.5" in sub_indices or "PM10" in sub_indices
    if len(sub_indices) < 3 or not has_pm:
        return None, None, None

    dominant = max(sub_indices, key=sub_indices.get)   # dict method use
    aqi = sub_indices[dominant]
    return aqi, dominant, get_category(aqi)


def get_health_advice(category):
    """Category ke hisaab se health advice."""
    return HEALTH_ADVICE.get(category, "No advice available.")
'''

# ---------------------------------------------------------------------
# MODULE 2 : data_manager  (Dataset + File Handling + CRUD)
# ---------------------------------------------------------------------
DATA_MANAGER_SRC = r'''
"""Module 2: Dataset creation, file handling and CRUD operations."""
import os
import random
import datetime
import pandas as pd
import aqi_calculator as ac

CSV_FILE = "aqi_dataset.csv"
COLUMNS = ["ID", "City", "Date", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3",
           "AQI", "Dominant", "Category"]

# City -> typical PM2.5 level (dataset realistic banane ke liye)
CITY_PROFILES = {"Delhi": 190, "Ghaziabad": 175, "Lucknow": 140, "Kanpur": 150,
                 "Mumbai": 70, "Kolkata": 110, "Chennai": 50, "Bengaluru": 45,
                 "Hyderabad": 65, "Jaipur": 100}

# ----- DATA STRUCTURE 5: SET (valid cities - duplicates nahi) -----
VALID_CITIES = set(CITY_PROFILES.keys())


def create_dataset(total=60, filename=CSV_FILE):
    """60 records ka AQI dataset banakar CSV file me save karta hai."""
    random.seed(42)                       # har baar same data
    cities = list(CITY_PROFILES.keys())   # list
    start = datetime.date(2026, 10, 1)
    rows = []                             # list of dicts

    for i in range(1, total + 1):
        city = cities[(i - 1) % len(cities)]
        base = CITY_PROFILES[city]
        pm25 = round(random.uniform(base * 0.6, base * 1.4), 1)
        record = {
            "ID": i,
            "City": city,
            "Date": (start + datetime.timedelta(days=i % 30)).isoformat(),
            "PM2.5": pm25,
            "PM10": round(pm25 * random.uniform(1.4, 2.0), 1),
            "NO2": round(random.uniform(15, 120), 1),
            "SO2": round(random.uniform(5, 60), 1),
            "CO": round(random.uniform(0.4, 6), 2),
            "O3": round(random.uniform(20, 120), 1),
        }
        # Kuch records me jaan-bujhkar missing values (cleaning practice ke liye)
        if i % 11 == 0:
            record["NO2"] = None
        if i % 17 == 0:
            record["SO2"] = None
        if i % 23 == 0:
            record["O3"] = None

        aqi, dominant, category = ac.calculate_aqi(record)
        record.update({"AQI": aqi, "Dominant": dominant, "Category": category})
        rows.append(record)

    pd.DataFrame(rows, columns=COLUMNS).to_csv(filename, index=False)
    return filename


def load_data(filename=CSV_FILE):
    """CSV file read karta hai (file na ho to pehle bana deta hai)."""
    if not os.path.exists(filename):
        create_dataset(filename=filename)
        print(f"[INFO] '{filename}' nahi mili, naya dataset (60 records) bana diya.")
    return pd.read_csv(filename)


def save_data(df, filename=CSV_FILE):
    """DataFrame ko CSV file me save karta hai."""
    df.to_csv(filename, index=False)


def get_next_id(df):
    """Naya unique ID."""
    return 1 if df.empty else int(df["ID"].max()) + 1


def add_record(df, city, date, readings):
    """Naya record add karta hai aur AQI khud calculate karta hai."""
    aqi, dominant, category = ac.calculate_aqi(readings)
    if aqi is None:
        return df, None
    new_row = {"ID": get_next_id(df), "City": city, "Date": date}
    for pollutant in ac.POLLUTANTS:
        new_row[pollutant] = readings.get(pollutant)
    new_row.update({"AQI": aqi, "Dominant": dominant, "Category": category})
    df = pd.concat([df, pd.DataFrame([new_row], columns=COLUMNS)], ignore_index=True)
    save_data(df)
    return df, new_row


def search_by_id(df, record_id):
    """ID se record dhoondhta hai."""
    return df[df["ID"] == record_id]


def search_by_city(df, city):
    """City se records dhoondhta hai (case-insensitive)."""
    return df[df["City"].str.lower() == city.strip().lower()]


def update_record(df, record_id, field, value):
    """Record ki field update karta hai; pollutant badle to AQI dobara nikalta hai."""
    if record_id not in df["ID"].values:
        return df, False
    idx = df.index[df["ID"] == record_id][0]
    df.loc[idx, field] = value
    if field in ac.POLLUTANTS:
        readings = {p: df.loc[idx, p] for p in ac.POLLUTANTS}
        aqi, dominant, category = ac.calculate_aqi(readings)
        df.loc[idx, ["AQI", "Dominant", "Category"]] = [aqi, dominant, category]
    save_data(df)
    return df, True


def delete_record(df, record_id):
    """Record delete karta hai."""
    if record_id not in df["ID"].values:
        return df, False
    df = df[df["ID"] != record_id].reset_index(drop=True)
    save_data(df)
    return df, True
'''

# ---------------------------------------------------------------------
# MODULE 3 : analysis_tools  (NumPy + Pandas analysis + Report)
# ---------------------------------------------------------------------
ANALYSIS_TOOLS_SRC = r'''
"""Module 3: NumPy, Pandas analysis and report generation."""
import numpy as np
import pandas as pd
import aqi_calculator as ac


def line(char="=", width=70):
    """Separator line."""
    return char * width


def heading(title):
    """Section heading print karta hai."""
    print("\n" + line())
    print(f"  {title}")
    print(line())


def numpy_analysis(df):
    """NumPy implementation: 1D/2D array, indexing, slicing, sum, mean, max, min, std."""
    heading("NUMPY ANALYSIS")

    # ---- 1D array ----
    aqi_1d = df["AQI"].dropna().to_numpy()
    print("1D Array (AQI values) shape :", aqi_1d.shape)
    print("First 10 values            :", aqi_1d[:10])

    # ---- 2D array ----
    cols = list(ac.POLLUTANTS)
    arr_2d = df[cols].to_numpy(dtype=float)
    print("\n2D Array (pollutants) shape :", arr_2d.shape, "-> (records, pollutants)")

    # ---- Indexing & slicing ----
    print("\n--- Indexing & Slicing ---")
    print("aqi_1d[0]  (pehla AQI)      :", aqi_1d[0])
    print("aqi_1d[-1] (aakhri AQI)     :", aqi_1d[-1])
    print("aqi_1d[5:10] (slice)        :", aqi_1d[5:10])
    print("arr_2d[0] (pehla record)    :", arr_2d[0])
    print("arr_2d[0:3, 0:2] (3 rows, PM2.5 & PM10):\n", arr_2d[0:3, 0:2])
    print("arr_2d[:, 0][:5] (PM2.5 col):", arr_2d[:5, 0])

    # ---- Sum / Mean / Max / Min / Std ----
    print("\n--- AQI Statistics (NumPy) ---")
    print(f"Sum               : {np.sum(aqi_1d)}")
    print(f"Mean (Average)    : {np.mean(aqi_1d):.2f}")
    print(f"Maximum           : {np.max(aqi_1d)}")
    print(f"Minimum           : {np.min(aqi_1d)}")
    print(f"Standard Deviation: {np.std(aqi_1d):.2f}")

    print("\n--- Pollutant-wise Statistics (2D, axis=0, NaN ignore) ---")
    print(f"{'Pollutant':<10}{'Mean':>10}{'Max':>10}{'Min':>10}{'Std':>10}")
    means = np.nanmean(arr_2d, axis=0)
    maxs = np.nanmax(arr_2d, axis=0)
    mins = np.nanmin(arr_2d, axis=0)
    stds = np.nanstd(arr_2d, axis=0)
    for i, name in enumerate(cols):
        print(f"{name:<10}{means[i]:>10.2f}{maxs[i]:>10.2f}{mins[i]:>10.2f}{stds[i]:>10.2f}")


def pandas_analysis(df):
    """Pandas implementation: DataFrame, read CSV, select, filter, sort, groupby, missing, stats."""
    heading("PANDAS ANALYSIS")

    # ---- Create a DataFrame (dictionary se) ----
    demo = pd.DataFrame({"Category": [c for _, c in ac.CATEGORIES],
                         "Max AQI": [limit for limit, _ in ac.CATEGORIES]})
    print("1) Naya DataFrame (AQI category scale):")
    print(demo.to_string(index=False))

    # ---- Selected rows & columns ----
    print("\n2) Selected rows & columns (pehle 5 records, City/Date/AQI/Category):")
    print(df.loc[0:4, ["City", "Date", "AQI", "Category"]].to_string(index=False))
    print("\n   iloc[10:13, 1:4]:")
    print(df.iloc[10:13, 1:4].to_string(index=False))

    # ---- Filtering ----
    severe = df[df["AQI"] > 300]
    print(f"\n3) Filtering -> AQI > 300 wale records: {len(severe)}")
    print(severe[["ID", "City", "AQI", "Category"]].head(8).to_string(index=False))
    delhi_poor = df[(df["City"] == "Delhi") & (df["AQI"] > 200)]
    print(f"   Delhi ke 'Poor ya worse' records: {len(delhi_poor)}")

    # ---- Sorting ----
    print("\n4) Sorting -> Top 5 sabse zyada AQI:")
    top5 = df.sort_values(by="AQI", ascending=False).head(5)
    print(top5[["ID", "City", "Date", "AQI", "Category"]].to_string(index=False))

    # ---- GroupBy ----
    print("\n5) GroupBy -> City wise AQI:")
    grouped = df.groupby("City")["AQI"].agg(["count", "mean", "max", "min"]).round(1)
    print(grouped.sort_values("mean", ascending=False).to_string())
    print("\n   GroupBy -> Category wise record count:")
    print(df.groupby("Category")["ID"].count().to_string())

    # ---- Missing values ----
    print("\n6) Missing values (cleaning se pehle):")
    print(df[list(ac.POLLUTANTS)].isnull().sum().to_string())
    clean = df.copy()
    for col in ac.POLLUTANTS:
        clean[col] = clean[col].fillna(clean[col].mean())    # mean se fill
    print("   Cleaning ke baad total missing:", int(clean[list(ac.POLLUTANTS)].isnull().sum().sum()))

    # ---- Statistical analysis ----
    print("\n7) Statistical analysis (describe):")
    print(clean[["PM2.5", "PM10", "NO2", "SO2", "CO", "O3", "AQI"]].describe().round(2).to_string())
    print("\n   Median AQI :", df["AQI"].median())
    print("   Variance   :", round(df["AQI"].var(), 2))


def generate_insights(df):
    """NumPy + Pandas se meaningful insights."""
    import numpy as np
    heading("DATA INSIGHTS")
    city_avg = df.groupby("City")["AQI"].mean()
    worst, best = city_avg.idxmax(), city_avg.idxmin()
    print(f"1. Sabse polluted city : {worst} (avg AQI {city_avg.max():.1f})")
    print(f"2. Sabse saaf city     : {best} (avg AQI {city_avg.min():.1f})")

    bad = np.sum(df["AQI"].to_numpy() > 200)
    print(f"3. {bad} records ({bad / len(df) * 100:.1f}%) me AQI 'Poor' ya usse kharab hai.")

    corr = df["PM2.5"].corr(df["AQI"])
    print(f"4. PM2.5 aur AQI ka correlation: {corr:.2f} (1 ke paas = bahut strong relation)")

    dominant = df["Dominant"].value_counts()
    print(f"5. Sabse zyada AQI badhane wala pollutant: {dominant.idxmax()} "
          f"({dominant.max()} records me dominant)")

    mode_cat = df["Category"].mode()[0]
    print(f"6. Sabse common category: {mode_cat}")

    cleaner = df[df["AQI"] <= 100]
    print(f"7. Sirf {len(cleaner)} records 'Good/Satisfactory' range me hain.")


def summary_report(df):
    """Poora summary report."""
    heading("AQI SUMMARY REPORT")
    print(f"Total records         : {len(df)}")
    print(f"Cities covered        : {df['City'].nunique()}")
    print(f"Date range            : {df['Date'].min()}  to  {df['Date'].max()}")
    print(f"Average AQI           : {df['AQI'].mean():.2f}")
    print(f"Highest AQI           : {int(df['AQI'].max())}  "
          f"({df.loc[df['AQI'].idxmax(), 'City']}, {df.loc[df['AQI'].idxmax(), 'Date']})")
    print(f"Lowest AQI            : {int(df['AQI'].min())}  "
          f"({df.loc[df['AQI'].idxmin(), 'City']}, {df.loc[df['AQI'].idxmin(), 'Date']})")
    print("\nCategory distribution:")
    counts = df["Category"].value_counts()
    for name, count in counts.items():
        bar = "#" * int(count / len(df) * 40)
        print(f"  {name:<13}{count:>4}  {bar}")
    print("\nCity wise average AQI:")
    for city, avg in df.groupby("City")["AQI"].mean().sort_values(ascending=False).items():
        print(f"  {city:<12}{avg:>8.1f}  [{ac.get_category(avg)}]")
'''


# ---------------------------------------------------------------------
# Modules ko create + register karna (taki `import` chal sake)
# ---------------------------------------------------------------------
def create_module(name, source):
    """String source se ek real Python module banakar sys.modules me register karta hai."""
    module = types.ModuleType(name)
    exec(compile(source, f"<{name}>", "exec"), module.__dict__)
    sys.modules[name] = module
    return module


create_module("aqi_calculator", AQI_CALCULATOR_SRC)
create_module("data_manager", DATA_MANAGER_SRC)
create_module("analysis_tools", ANALYSIS_TOOLS_SRC)

# ---- 3 separate modules ko import karna ----
import aqi_calculator as ac          # noqa: E402
import data_manager as dm            # noqa: E402
import analysis_tools as at          # noqa: E402

import pandas as pd                  # noqa: E402
import datetime                      # noqa: E402

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)


# ---------------------------------------------------------------------
# MAIN PROGRAM : user input helpers + menu
# ---------------------------------------------------------------------
def read_float(prompt):
    """Float input; blank chhodne par None (missing) return karta hai."""
    while True:
        text = input(prompt).strip()
        if text == "":
            return None
        try:
            value = float(text)
            if value < 0:
                print("  Negative value allowed nahi hai.")
                continue
            return value
        except ValueError:
            print("  Sahi number daalein (ya khaali chhod dein).")


def read_int(prompt):
    """Integer input."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("  Sahi integer daalein.")


def read_date(prompt):
    """Date input (YYYY-MM-DD); blank = aaj ki date."""
    while True:
        text = input(prompt).strip()
        if text == "":
            return datetime.date.today().isoformat()
        try:
            return datetime.date.fromisoformat(text).isoformat()
        except ValueError:
            print("  Format YYYY-MM-DD hona chahiye.")


def read_readings():
    """Saare pollutants ki values leta hai aur dictionary return karta hai."""
    print("Pollutant values daalein (unit: ug/m3, CO ke liye mg/m3). Missing ho to Enter dabayein.")
    readings = {}
    for pollutant in ac.POLLUTANTS:
        readings[pollutant] = read_float(f"  {pollutant}: ")
    return readings


def show_table(data):
    """DataFrame ko neat table me dikhata hai."""
    if data.empty:
        print("  Koi record nahi mila.")
    else:
        print(data.fillna("-").to_string(index=False))


def show_aqi_result(aqi, dominant, category):
    """AQI result ka formatted output."""
    print("\n" + at.line("-", 50))
    print(f"  AQI Value          : {aqi}")
    print(f"  Category           : {category}")
    print(f"  Dominant Pollutant : {dominant}")
    print(f"  Health Advice      : {ac.get_health_advice(category)}")
    print(at.line("-", 50))


def menu_add(df):
    """1) Naya record add karo."""
    at.heading("ADD NEW RECORD")
    city = input("City ka naam: ").strip().title()
    if not city:
        print("City khaali nahi ho sakti.")
        return df
    if city not in dm.VALID_CITIES:
        print(f"  (Note: '{city}' dataset ki existing cities me nahi hai, phir bhi add hoga.)")
    date = read_date("Date (YYYY-MM-DD, Enter = aaj): ")
    readings = read_readings()
    df, row = dm.add_record(df, city, date, readings)
    if row is None:
        print("\n[ERROR] AQI nahi nikal sakta: kam se kam 3 pollutants (PM2.5 ya PM10 ke saath) chahiye.")
    else:
        print(f"\n[OK] Record add ho gaya (ID = {row['ID']}).")
        show_aqi_result(row["AQI"], row["Dominant"], row["Category"])
    return df


def menu_display(df):
    """2) Saare records dikhao."""
    at.heading(f"ALL RECORDS ({len(df)})")
    show_table(df)


def menu_search(df):
    """3) Record search karo."""
    at.heading("SEARCH RECORD")
    choice = input("Search by  1) ID   2) City : ").strip()
    if choice == "1":
        show_table(dm.search_by_id(df, read_int("ID: ")))
    elif choice == "2":
        show_table(dm.search_by_city(df, input("City: ")))
    else:
        print("Galat option.")


def menu_update(df):
    """4) Record update karo."""
    at.heading("UPDATE RECORD")
    record_id = read_int("Jis record ka ID update karna hai: ")
    show_table(dm.search_by_id(df, record_id))
    if dm.search_by_id(df, record_id).empty:
        return df

    editable = list(ac.POLLUTANTS) + ["City", "Date"]       # list
    print("Update ho sakne wali fields:", ", ".join(editable))
    field = input("Field ka naam: ").strip()
    matched = [f for f in editable if f.lower() == field.lower()]
    if not matched:
        print("Galat field.")
        return df
    field = matched[0]
    if field in ac.POLLUTANTS:
        value = read_float(f"Naya {field} value: ")
        if value is None:
            print("Value khaali nahi ho sakti.")
            return df
    elif field == "Date":
        value = read_date("Nayi date (YYYY-MM-DD): ")
    else:
        value = input("Naya city naam: ").strip().title()

    df, done = dm.update_record(df, record_id, field, value)
    print("[OK] Record update ho gaya." if done else "[ERROR] Update fail.")
    show_table(dm.search_by_id(df, record_id))
    return df


def menu_delete(df):
    """5) Record delete karo."""
    at.heading("DELETE RECORD")
    record_id = read_int("Jis record ka ID delete karna hai: ")
    show_table(dm.search_by_id(df, record_id))
    if dm.search_by_id(df, record_id).empty:
        return df
    if input("Pakka delete karein? (y/n): ").strip().lower() == "y":
        df, done = dm.delete_record(df, record_id)
        print("[OK] Record delete ho gaya." if done else "[ERROR] Delete fail.")
    else:
        print("Delete cancel kiya.")
    return df


def menu_quick_aqi():
    """9) AQI Generator: values daalo, AQI pao (dataset me save nahi hota)."""
    at.heading("QUICK AQI GENERATOR")
    readings = read_readings()
    aqi, dominant, category = ac.calculate_aqi(readings)
    if aqi is None:
        print("\n[ERROR] Kam se kam 3 pollutants (PM2.5 ya PM10 ke saath) chahiye.")
        return
    sub = {p: ac.calculate_sub_index(p, v) for p, v in readings.items()}
    print("\nSub-index (pollutant wise):")
    for pollutant, value in sub.items():                    # dict.items()
        print(f"  {pollutant:<6}: {value if value is not None else '-'}")
    show_aqi_result(aqi, dominant, category)


def show_menu():
    """Main menu."""
    print("\n" + at.line("="))
    print("        AQI GENERATOR & ANALYZER  -  MAIN MENU")
    print(at.line("="))
    items = [
        "Add new record",
        "Display all records",
        "Search a record",
        "Update a record",
        "Delete a record",
        "Summary report",
        "NumPy analysis",
        "Pandas analysis",
        "Quick AQI generator (without saving)",
        "Data insights",
    ]
    for number, text in enumerate(items, start=1):
        print(f"  {number:>2}. {text}")
    print("   0. Exit")
    print(at.line("-"))


def main():
    """Program ka entry point."""
    df = dm.load_data()                                     # file handling (CSV read)
    print(f"[INFO] Dataset load hua: {len(df)} records, {len(df.columns)} columns "
          f"('{dm.CSV_FILE}')")

    actions = {                                             # dict of menu -> function
        "2": lambda: menu_display(df),
        "3": lambda: menu_search(df),
        "6": lambda: at.summary_report(df),
        "7": lambda: at.numpy_analysis(df),
        "8": lambda: at.pandas_analysis(df),
        "9": menu_quick_aqi,
        "10": lambda: at.generate_insights(df),
    }

    while True:
        show_menu()
        choice = input("Apna option chunein: ").strip()
        if choice == "0":
            print("\nDhanyavaad! Program band ho gaya.")
            break
        elif choice == "1":
            df = menu_add(df)
        elif choice == "4":
            df = menu_update(df)
        elif choice == "5":
            df = menu_delete(df)
        elif choice in actions:
            actions[choice]()
        else:
            print("Galat option, dobara try karein.")
        input("\nContinue karne ke liye Enter dabayein...")


if __name__ == "__main__":
    main()