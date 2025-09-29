class ParametersSelection:
    def __init__(self):
        self.params = []

    def add_equal(self, field_name: str, value, value_type: type, symbol='='):
        if value_type == int:
            self.params.append({'field_name': field_name, 'symbol': symbol, 'value': value})
        elif value_type == bool:
            self.params.append({'field_name': field_name, 'symbol': symbol, 'value': str(int(value))})
        else:
            self.params.append({'field_name': field_name, 'symbol': symbol, 'value': f'"{value}"'})

    def add_inequal(self, field_name: str, value, more_less: bool, and_equal: bool, value_type: type):
        symbol = ''

        if more_less:
            symbol = '>'
        elif not more_less:
            symbol = '<'

        if and_equal:
            symbol = f'{symbol}='

        self.add_equal(field_name, value, value_type, symbol)

    def get_parameters_selection(self):
        result = []
        for param in self.params:
            result.append(f'{param['field_name']} {param['symbol']} {param['value']}')
        return result

# p = ParametersSelection()
# p.add_inequal("1",False, False, True, bool)
# print(p.params)