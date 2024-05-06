#
# this class was generated automatically by chatgpt
#
class MultiMap:
    def __init__(self):
        self._data = {}

    def __setitem__(self, key, value):
        float_key = float(key)
        if float_key in self._data:
            self._data[float_key].append(value)
        else:
            self._data[float_key] = [value]

    def __getitem__(self, key):
        return self._data[float(key)]

    def __delitem__(self, key):
        del self._data[float(key)]

    def __contains__(self, key):
        return float(key) in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

# Example usage
# float_dict = MulDict()
# float_dict[1.0] = 'value1'
# float_dict[1.0] = 'value2'  # Adding another value for the same key
# float_dict[2.5] = 'value3'

# print(float_dict[1])  # Output: ['value1', 'value2']
# print(float_dict[2.5])  # Output: ['value3']

# # Keys can be integers or floats, they will be converted to floats internally
# print(1 in float_dict)  # Output: True
# print(2.0 in float_dict)  # Output: True

# # Iterating over keys, values, or items
# for key in float_dict:
#     print(key)

# for value in float_dict.values():
#     print(value)

# for key, value in float_dict.items():
#     print(key, value)

# # Deleting a key
# del float_dict[1.0]
# print(list(float_dict.keys()))  # Output: [2.5]
