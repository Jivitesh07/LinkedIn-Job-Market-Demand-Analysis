import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter

def scrape_jobs(keyword, location):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    job_data = []

    # Collect 50 jobs (25 per page → 2 pages)
    for start in range(0, 50, 25):

        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location={location}&start={start}"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        jobs = soup.find_all("div", class_="base-search-card")

        for job in jobs:
            title = job.find("h3", class_="base-search-card__title")
            company = job.find("h4", class_="base-search-card__subtitle")
            location = job.find("span", class_="job-search-card__location")

            job_data.append({
                "Role": title.text.strip() if title else None,
                "Company": company.text.strip() if company else None,
                "Location": location.text.strip() if location else None
            })

    # Keep only first 50 rows
    df = pd.DataFrame(job_data).head(50)

    # Save CSV
    df.to_csv("linkedin_jobs.csv", index=False)

    print("CSV file saved: linkedin_jobs.csv")

    # ----------- Excel Visualization -----------

    # Count job roles
    role_counts = Counter(df["Role"])
    role_df = pd.DataFrame(role_counts.items(), columns=["Role", "Count"])

    with pd.ExcelWriter("linkedin_jobs_analysis.xlsx", engine="xlsxwriter") as writer:

        df.to_excel(writer, sheet_name="Raw Data", index=False)
        role_df.to_excel(writer, sheet_name="Analysis", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Analysis"]

        chart = workbook.add_chart({"type": "column"})

        chart.add_series({
            "name": "Job Count",
            "categories": "=Analysis!$A$2:$A$10",
            "values": "=Analysis!$B$2:$B$10",
        })

        chart.set_title({"name": "Top Job Roles"})
        chart.set_x_axis({"name": "Role"})
        chart.set_y_axis({"name": "Count"})

        worksheet.insert_chart("D2", chart)

    print("Excel file with visualization saved: linkedin_jobs_analysis.xlsx")

    return df


# Run scraper
scrape_jobs("Software Engineer", "India")