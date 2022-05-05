def build_submit(smedge_submit=None, script=True, *args, **kwargs) -> str:
    """
    Creates a submission command from all the given input values. Keys are case-sensitive so
    if they need to be capitalised they should be capitalised as the input key.

    If a value starts with an underscore then it will be treated as a property and will not
    wrap it into a string.

    :smedgeSubmit:  :str:   Location of where the smedge submit executable is.
    """
    if smedge_submit is None:
        smedge_submit = 'C:/Program Files/Smedge/Submit.exe'

    _construct = smedge_submit
    if script:
        _construct += ' Script'

    def _format_data(data) -> str:
        # Formats data to be a string or data type
        if isinstance(data, str):
            return f'"{data}"'
        return f'{data}'

    def _deconstruct_list(ls: list):
        _a = ''
        if ls is None:
            return ''
        for i in ls:
            if len(_a) > 0:
                _a += ' '
            _a += _format_data(i)
        return _a

    def _input(prop: str = None, val=None):
        _data = ''
        _val = _format_data(val) if not isinstance(val, list) else _deconstruct_list(val)
        return f'{prop} {_val}' if prop is not None else f'{_val}'

    for a in args:
        if len(_construct) > 0:
            _construct += ' '
        _construct += _input(None, a)

    for key in kwargs:
        name = key
        val = kwargs[key]
        if len(_construct) > 0:
            _construct += ' '
        if name.startswith('_'):
            _construct += val
            continue
        _construct += _input(name, val)
    return _construct
