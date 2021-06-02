parquet_write_kwargs = {
    'engine': 'fastparquet',
    'compression': 'gzip',
    'row_group_offsets': 5000000
}

parquet_read_kwargs = {
    'engine': 'fastparquet'
}
