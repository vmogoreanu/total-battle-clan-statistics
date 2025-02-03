import pygsheets
import pandas as pd
import pandasql as ps
import datetime
from datetime import timedelta

todayDate = datetime.date.today()
mondayDate = todayDate + datetime.timedelta(days=-todayDate.weekday())
start = datetime.datetime(mondayDate.year, mondayDate.month, mondayDate.day)
end = start + timedelta(days = 7) - timedelta(seconds=1)
rangestr = start.strftime("%Y-%m-%d") + " to " + end.strftime("%Y-%m-%d")
start = start - timedelta(hours=3) # correction for Russian time zone
startstr = start.isoformat()
endstr = end.isoformat()

print("Period: " + rangestr)
print("start time: " + startstr)
print("end time: " + endstr)

df = pd.read_csv("data.csv",encoding='latin-1')
dfs = pd.read_csv("sourceScore.csv",encoding='latin-1')
dft = pd.read_csv("typeScore.csv",encoding='latin-1')
dfa = pd.read_csv("accounts.csv",encoding='latin-1')

query = "SELECT df.account, df.type, df.source, "\
            " CASE WHEN df.source LIKE '%citadel%' THEN 1 ELSE 0 END AS citadel, "\
            " CASE WHEN df.source LIKE '%crypt%' THEN 1 ELSE 0 END AS crypt, "\
            " CASE WHEN NOT dfs.score is NULL THEN dfs.score "\
            "   WHEN dfs.score is NULL AND NOT dft.score is NULL THEN dft.score "\
            "   ELSE 0 END AS score "\
            " FROM df LEFT JOIN dfs on df.source=dfs.source "\
            " LEFT JOIN dft on df.type=dft.type "\
            " WHERE time >= '" + startstr +"' AND "\
                " time <= '" + endstr + "' "

df = ps.sqldf(query, locals())
print(query)
query = "SELECT account as [Игрок Account], sum(citadel) as [Цитадели Citadels], sum(crypt) as [Склепы Crypts], "\
        " count(*) as [Cундуки Chests], SUM(score) as [Очки Score]  "\
            " FROM df GROUP BY account "
df = ps.sqldf(query, locals())


query = "SELECT * FROM df "\
        " UNION ALL "\
        "SELECT account, 0, 0, 0, 0 FROM dfa WHERE NOT account IN (SELECT [Игрок Account] FROM df)"
df = ps.sqldf(query, locals())

df = df.sort_values(by="Очки Score", ascending=False)

print("saving locally")
df.to_csv(rangestr + ".csv", index=False)

print("uploading to Google Sheets: " + rangestr)
client = pygsheets.authorize(service_account_file="service_account.json")
sh = client.open('EFR stats')

try:
  wks = sh.add_worksheet(rangestr)
except:
  pass

wks = sh.worksheet_by_title(rangestr)
wks.clear()
wks.set_dataframe(df, (1, 1))

print("Completed")