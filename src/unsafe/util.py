def ensure_fd_id_index(df, name):
    """
    Ensure a dataframe is indexed by the structure identifier.

    Parameters
    ----------
    df : pandas.DataFrame or geopandas.GeoDataFrame
        Dataframe to check.

    name : str
        Name of the dataframe used in error messages.

    Returns
    -------
    pandas.DataFrame or geopandas.GeoDataFrame
        The input dataframe indexed by ``fd_id``.

    Raises
    ------
    ValueError
        If the dataframe is neither indexed by ``fd_id`` nor
        contains an ``fd_id`` column.
    """

    # Nothing to do if the dataframe was not supplied.
    if df is None:
        return None

    # Already indexed correctly.
    if df.index.name == "fd_id":
        return df

    # Promote the structure identifier to the index.
    if "fd_id" in df.columns:
        return df.set_index("fd_id")

    raise ValueError(
        f"{name} must either be indexed by 'fd_id' "
        "or contain an 'fd_id' column."
    )