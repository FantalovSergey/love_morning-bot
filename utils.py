def get_indexes(text: str) -> list[int]:
    index_ranges = text.split(', ')
    indexes = []
    for index_range in index_ranges:
        if '-' in index_range:
            start_index, stop_index = index_range.split('-')
            for index in range(int(start_index), int(stop_index) + 1):
                indexes.append(index)
        else:
            indexes.append(int(index_range))
    return indexes
