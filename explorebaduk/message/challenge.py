NO_UNDO = 1000
NO_PAUSE = 100
NO_ANALYZE = 10
IS_PRIVATE = 1


def make_restrictions_string(restrictions: dict):
    initial_string = ''

    for item in ['no_undo', 'no_pause', 'no_analyze', 'is_private']:
        initial_string += str(int(bool(restrictions[item])))

    return initial_string


print(make_restrictions_string({
            'no_undo': False,
            'no_pause': False,
            'no_analyze': False,
            'is_private': False,
        }))