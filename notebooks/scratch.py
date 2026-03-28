import marimo

__generated_with = "0.14.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Scratch notebook

        Use this for quick exploration.

        Rules of thumb:
        - keep reusable logic in `src/`
        - keep notebooks thin
        - write down assumptions
        - promote stable code out of the notebook
        """
    )
    return


if __name__ == "__main__":
    app.run()
