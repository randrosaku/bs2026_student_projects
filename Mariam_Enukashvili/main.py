import pandas as pd
import matplotlib.pyplot as plt

def main():
    # load dataset
    file_path = "data/raw/startups.csv"
    df = pd.read_csv(file_path)

    # show first rows
    print("\nFirst 5 rows:")
    print(df.head())

    # show column names
    print("\nColumns:")
    print(df.columns.tolist())

    # show dataset shape
    print("\nDataset shape (rows, columns):")
    print(df.shape)

    # check missing values
    print("\nMissing values:")
    print(df.isnull().sum())

    # Top countries
    print("\nTop countries:")
    top_countries = df["Country"].value_counts().head(10)
    print(top_countries)

    # Create bar chart for top countries
    plt.figure(figsize=(10, 6))
    top_countries.plot(kind="bar")
    plt.title("Top 10 Countries by Number of Startups")
    plt.xlabel("Country")
    plt.ylabel("Number of Startups")
    plt.tight_layout()
    plt.savefig("results/top_10_countries.png")
    plt.show()

    # Top industries
    print("\nTop industries:")
    top_industries = df["Industry"].value_counts().head(10)
    print(top_industries)

    # Create bar chart for top industries
    plt.figure(figsize=(10, 6))
    top_industries.plot(kind="bar")
    plt.title("Top 10 Industries by Number of Startups")
    plt.xlabel("Industry")
    plt.ylabel("Number of Startups")
    plt.tight_layout()
    plt.savefig("results/top_10_industries.png")
    plt.show()

    # Funding by year
    print("\nFunding by year:")
    funding_by_year = df.groupby("Founded Year")["Total Funding ($M)"].sum()
    print(funding_by_year.sort_index())

    # Create line chart for funding over time
    plt.figure(figsize=(10, 6))
    funding_by_year.sort_index().plot(kind="line", marker="o")
    plt.title("Total Funding by Year")
    plt.xlabel("Year")
    plt.ylabel("Total Funding ($M)")
    plt.tight_layout()
    plt.savefig("results/funding_trend.png")
    plt.show()

    # Top 5 startups by funding
    print("\nTop 5 funded startups:")
    top_funded = df.sort_values(by="Total Funding ($M)", ascending=False)
    print(top_funded[["Startup Name", "Country", "Industry", "Total Funding ($M)"]].head(5))

if __name__ == "__main__":
    main()