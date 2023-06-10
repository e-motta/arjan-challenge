import asyncio

# import plotly.express as px

from service import (
    get_countries,
    get_countries_as_df,
    get_populations_as_df,
    join_population_and_countries_df,
)


async def main() -> None:
    COUNTRIES_LIST = ["FRA", "BRA"]

    countries = await get_countries(COUNTRIES_LIST)
    countries_df = await get_countries_as_df(COUNTRIES_LIST)
    populations_df = get_populations_as_df([c.id for c in countries])

    # plot_df = join_population_and_countries_df(countries_df, populations_df)

    # fig = px.line(plot_df, x="year", y="population", color="name")
    # fig.update_layout(xaxis_title="Year", yaxis_title="Population")
    # fig.show()


if __name__ == "__main__":
    asyncio.run(main())
