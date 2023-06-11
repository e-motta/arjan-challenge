import asyncio
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import pandas as pd
from typing import List

from service import (
    get_countries,
    get_countries_as_df,
    get_populations_as_df,
    join_population_and_countries_for_plotting_df,
    get_countries_rel,
)


def main() -> None:
    app = Dash(__name__)
    server = app.server

    app.layout = html.Div(
        [
            html.H4("Country populations by year"),
            dcc.Dropdown(
                id="dropdown",
                options=get_countries_rel(),
                value=["NLD"],
                multi=True,
            ),
            dcc.Graph(id="graph"),
        ]
    )

    async def update_graph(countries_list: List[str]):
        if len(countries_list) > 0:
            countries = await get_countries(countries_list)
            countries_df = await get_countries_as_df(countries_list)
            populations_df = get_populations_as_df([c.id for c in countries])

            plot_df = join_population_and_countries_for_plotting_df(
                countries_df, populations_df
            )

        else:
            plot_df = pd.DataFrame({"year": [], "population": [], "Country": []})

        fig = px.line(plot_df, x="year", y="population", color="Country")
        fig.update_layout(xaxis_title="Year", yaxis_title="Population")
        return fig

    @app.callback(Output("graph", "figure"), Input("dropdown", "value"))
    def initiate_async_update(countries_list: List[str]):
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(update_graph(countries_list))
        loop.close()
        return result

    app.run()


if __name__ == "__main__":
    asyncio.run(main())
