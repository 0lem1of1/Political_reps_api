import os
import psycopg2
import requests
from bs4 import BeautifulSoup
from psycopg2 import sql
import datetime
import re

DB_NAME = os.getenv("POSTGRES_DB", "civic_tracker")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_SERVER", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

def upsert_data(cursor, table, columns, conflict_target, values, return_column='id'):
    insert_cols = sql.SQL(', ').join(map(sql.Identifier, columns))
    conflict_cols = sql.SQL(', ').join(map(sql.Identifier, conflict_target))
    update_assignments = [sql.SQL("{0} = EXCLUDED.{0}").format(sql.Identifier(col)) for col in columns if col not in conflict_target]
    
    query_parts = [
        sql.SQL("INSERT INTO {table} ({insert_cols}) VALUES %s ON CONFLICT ({conflict_cols})").format(
            table=sql.Identifier(table), insert_cols=insert_cols, conflict_cols=conflict_cols
        )
    ]
    
    if update_assignments:
        update_clause = sql.SQL(', ').join(update_assignments)
        query_parts.append(sql.SQL("DO UPDATE SET {update_clause}").format(update_clause=update_clause))
    else:
        query_parts.append(sql.SQL("DO NOTHING"))
        
    if return_column:
        query_parts.append(sql.SQL("RETURNING {return_col}").format(return_col=sql.Identifier(return_column)))

    final_query = sql.SQL(" ").join(query_parts)
    cursor.execute(final_query, (values,))
    
    if return_column:
        result = cursor.fetchone()
        return result[0] if result else None
    return None

def get_geo_info_from_zip(zip_code):
    print(f"Looking up geographic info for ZIP {zip_code}...")
    try:
        response = requests.get(f"https://api.zippopotam.us/us/{zip_code}")
        response.raise_for_status()
        data = response.json()
        place = data['places'][0]
        return { "city": place['place name'], "state_long": place['state'], "state_short": place['state abbreviation'] }
    except Exception as e:
        print(f"Could not get geo info for ZIP {zip_code}: {e}")
        return None

def fetch_house_representative(zip_code):
    print(f"Fetching House Representative for {zip_code}...")
    try:
        response = requests.get("https://ziplook.house.gov/htbin/findrep_house", params={'ZIP': zip_code}, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        name_tag = soup.select_one('#RepInfo a')
        name = name_tag.text.strip() if name_tag else None

        district_text = None
        text_node = soup.find(string=re.compile("is located in the"))
        if text_node:
            paragraph_tag = text_node.find_parent("p")
            district_text = paragraph_tag.get_text(strip=True)

        if name and district_text:
            print(f"--> Found House Rep: {name}")
            return {"name": name, "district_text": district_text}
        return None
    except Exception as e:
        print(f"Could not fetch House Representative: {e}")
        return None

def fetch_senators(state_short):
    print(f"Fetching Senators for {state_short}...")
    try:
        url = f"https://www.senate.gov/states/{state_short}/intro.htm"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        name_tags = soup.select('div.state-column strong a')
        senators = [tag.text.strip() for tag in name_tags]
        print(f"--> Found Senators: {senators}")
        return senators
    except Exception as e:
        print(f"Could not fetch Senators: {e}")
        return []

def fetch_governor(state_long):
    print(f"Fetching Governor for {state_long}...")
    try:
        state_slug = state_long.lower().replace(' ', '-')
        url = f"https://www.nga.org/governors/{state_slug}/"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        name_tag = soup.find('h1', class_='title--no-border', string=re.compile(r'^Gov\.'))
        governor_name = None 
        if name_tag:
            full_title_and_name = name_tag.text.strip()
            name_parts = full_title_and_name.split(' ', 1)
            if len(name_parts) > 1:
                governor_name = name_parts[1]
                print(f"--> Found Governor: {governor_name}")
        return governor_name
    except Exception as e:
        print(f"Could not fetch Governor: {e}")
        return None

def run_agent_for_zip(zip_code):
    now = datetime.datetime.now()
    print("--- Civic Tracker initialized ---")

    geo_info = get_geo_info_from_zip(zip_code)
    if not geo_info: return

    house_rep_info = fetch_house_representative(zip_code)
    senator_names = fetch_senators(geo_info['state_short'])
    governor_name = fetch_governor(geo_info['state_long'])

    all_numbers_found = re.findall(r'(\d+)', house_rep_info['district_text'])    
    district_number = int(all_numbers_found[1])

    district_id = f"{geo_info['state_short']}-{district_number:02d}"

    geography_data = { "zip_code": zip_code, "city": geo_info['city'], "state_short": geo_info['state_short'], "state_long": geo_info['state_long'], "congressional_district": district_id }
    reps_data = []
    reps_data.append({"name": house_rep_info['name'], "title": "U.S. House Representative"})
    for name in senator_names:
        reps_data.append({"name": name, "title": "U.S. Senator"})
    reps_data.append({"name": governor_name, "title": "Governor"})


    conn = get_db_connection()
    cur = conn.cursor()
    print("\nStoring all collected data in the database (zip_code as PK)...")
    geography_zip = upsert_data(cur, 'geography',
                                ['zip_code', 'city', 'state', 'district'],
                                ['zip_code'],
                                (geography_data['zip_code'], geography_data['city'], geography_data['state_long'], district_id),
                                return_column='zip_code')
    if geography_zip:
        for rep in reps_data:
            if "House" in rep['title'] or "Senator" in rep['title']:
                branch = "Federal"
            else: # Governor
                branch = "State"
            
            full_title = rep['title']
            if "House" in rep['title']: full_title = f"U.S. House Rep, {district_id}"
            elif "Senator" in rep['title']: full_title = f"U.S. Senator, {geo_info['state_short']}"
            elif "Governor" in rep['title']: full_title = f"Governor, {geo_info['state_long']}"
            representative_id = upsert_data(cur, 'representatives',
                                          ['name', 'title', 'branch'],
                                          ['name'],
                                          (rep['name'], full_title, branch))
            if representative_id:
                upsert_data(cur, 'rep_geography_map',
                            ['representative_id', 'geography_zip_code'],
                            ['representative_id', 'geography_zip_code'],
                            (representative_id, geography_zip),
                            return_column=None)
    conn.commit()
    print("\n--- Data insertion successful! ---")

    if conn:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_agent_for_zip(zip_code="11355")

