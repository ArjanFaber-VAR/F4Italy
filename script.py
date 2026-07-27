from io import BytesIO
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pdfplumber
import os
from urllib.parse import urlparse
import pandas as pd 
import psycopg2
import easyocr



years = ['2022', '2023', '2024', '2025', '2026']
pdfs = []
for y in years: 
    url = "https://www.acisport.it/it/F4/calendario-e-risultati/"+y

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")


    for link in soup.find_all("a", href=True):
        href = link["href"]
        if 'classifiche' in href and  href != 'https://www.acisport.it/it/F4/classifiche/2026':
            full_url = urljoin(url, href)
            
            url = full_url

            headers = {
                        "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            
            for link2 in soup.find_all("a", href=True):
                href2 = link2["href"]
                if 'pdf' in href2:
                    pdfs.append(href2)
                
                   
    print("Year "+y+" done")

lst = []
for i in pdfs:
    name = i.lower()
    if 'qualifying' in name:
        lst.append(i)
    if ('race' in i or 'gara' in name ) and not 'report' in name:
        lst.append(i)
    if 'practice' in i or 'Libere' in name:
        lst.append(i)

for i in lst:
    name = i.lower()
    if 'report' in name:
        lst.remove(i)

from io import BytesIO

def download_pdf(url):
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    with pdfplumber.open(BytesIO(response.content)) as pdf:
        page = pdf.pages[0]
        table = page.extract_table()

    df = pd.DataFrame(table[1:], columns=table[0])

    return df


for pdf in pdfs:
    try:
        print(f"Processing: {pdf}")

        df = download_pdf(pdf)
        df = df.dropna()
        print(df.columns)
        if len(df.columns) < 4:
            continue

        pdf_name = os.path.basename(urlparse(pdf).path).lower()
        if 'qualifying' in pdf_name:
            print("Quali")
            print(len(df.columns))
            try:
                df = df.iloc[:, [0, 1, 3, 4, 8, 11, 12, 17, 16, 13]]
            except Exception as e:
                print(f"Error: {e}")     
            conn = psycopg2.connect(
                host="ep-long-glitter-at9v26w9-pooler.c-9.us-east-1.aws.neon.tech",
                database="neondb",
                user="neondb_owner",
                password="npg_P6OimSTt9ngC",
                port=5432,
                sslmode="require"
            )

            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS f4_qualifying (
                class TEXT,
                num TEXT,
                driver TEXT,
                nat TEXT,
                team TEXT,
                vehicle TEXT,                
                lap TEXT,
                best_time TEXT,
                kph TEXT,
                time TEXT
            )
            """)
            conn.commit()
            insert_query = """
            INSERT INTO f4_qualifying (
                class, num, driver, nat,team,
                vehicle, lap, best_time, 
                kph, time 
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cur.executemany(insert_query, df.values.tolist())
            conn.commit()
            print(f"Inserted {len(df)} rows.")
        
            cur.close()
            conn.close()

            print("Done importing quali session data for FREC.")
            
            
        if ('race' in pdf_name or 'gara' in pdf_name ) and not 'report' in pdf_name:
            print("race")
            print(len(df.columns))
            try:
                df = df.iloc[:, [0, 1, 3, 4, 8, 11, 12, 17, 16, 13]]
            except Exception as e:
                print(f"Error: {e}")          
            conn = psycopg2.connect(
                host="ep-long-glitter-at9v26w9-pooler.c-9.us-east-1.aws.neon.tech",
                database="neondb",
                user="neondb_owner",
                password="npg_P6OimSTt9ngC",
                port=5432,
                sslmode="require"
            )

            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS f4_race (
                class TEXT,
                num TEXT,
                driver TEXT,
                nat TEXT,
                team TEXT,
                vehicle TEXT,                
                lap TEXT,
                best_time TEXT,
                kph TEXT,
                time TEXT
            )
            """)
            conn.commit()

            insert_query = """
            INSERT INTO f4_race (
                class, num, driver, nat,team,
                vehicle, lap, best_time, 
                kph, time 
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cur.executemany(insert_query, df.values.tolist())
            conn.commit()
            print(f"Inserted {len(df)} rows.")

            cur.close()
            conn.close()
        if 'practice' in pdf_name or 'Libere' in pdf_name:
            print("practice")
            print(len(df.columns))
            try:
                df = df.iloc[:, [0, 1, 3, 4, 8, 11, 12, 17, 16, 13]]
            except Exception as e:
                print(f"Error: {e}")     
            conn = psycopg2.connect(
                host="ep-long-glitter-at9v26w9-pooler.c-9.us-east-1.aws.neon.tech",
                database="neondb",
                user="neondb_owner",
                password="npg_P6OimSTt9ngC",
                port=5432,
                sslmode="require"
            )

            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS f4_practice(
                class TEXT,
                num TEXT,
                driver TEXT,
                nat TEXT,
                team TEXT,
                vehicle TEXT,                
                lap TEXT,
                best_time TEXT,
                kph TEXT,
                time TEXT
            )
            """)
            conn.commit()

            insert_query = """
            INSERT INTO f4_practice (
                class, num, driver, nat,team,
                vehicle, lap, best_time, 
                kph, time 
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cur.executemany(insert_query, df.values.tolist())
            conn.commit()
            print(f"Inserted {len(df)} rows.")

            cur.close()
            conn.close()

    except Exception as e:
        print(f"Failed to process {pdf}")
        print(f"Error: {e}")

        # Close the database connection if it was opened

        continue
