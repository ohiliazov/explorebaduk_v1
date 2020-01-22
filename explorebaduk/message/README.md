## Message examples
    <message_type> <action> <input_data>

### Message type: AUTH

#### Login
    auth login <user_id> <token>
    auth login 1234 kvmCATy7Xm2CnHptmsyVFzjGZeqyoSeoFkf6cIjQyYJWRBNzYqAhXX4oJBMdHMZ2

##### Responses
    OK auth login: logged in
    ERROR auth login: already logged in
    ERROR auth login: user not found
    ERROR auth login: invalid token

#### Logout
    auth logout

##### Responses
    OK auth logout: logged out
    ERROR auth logout: not logged in


### Challenge examples

#### Input data
      game_type = 0 (0=ranked, 1=free, etc.)
          rules = 0 (0=japanese, 1=chinese, etc.)
    players_num = 2 (number of players to play in the game)

    game_info = GT<game_type>RL<rules>PL<players_num>
    game_info = GT0RL0PL2

    board_size = 19:19
    
       undo = 1 (1=yes, 0=no)
      pause = 0 (1=yes, 0=no)
    is_open = 1 (1=yes, 0=no)

    flags = F<undo><pause><is_open>
    flags = F101

    time_system = 2 (0=none, 1=absolute, 2=byoyomi, 3=canadian, 4=fischer, 5=custom)
      main_time = 3600 (seconds) - main time per player
       overtime = 30 (seconds) - time per overtime period
        periods = 5 - number of periods (valid for byoyomi and custom time system)
         stones = 1 - number of stones (valid for canadian and custom time system)
          bonus = 0 (seconds) - time increment per move (valid for fischer and custom time system)
          delay = 0 (seconds) - time to wait before start time countdown

    time_settings = T<time_system>M<main_time>O<overtime>P<periods>S<stones>B<bonus>D<delay>
    time_settings = T2M3600O30P5S1B0D0

    name = My Challenge

#### Output data
    challenge_id = 713

#### New challenge
    challenge new <game_info> <board_size> <flags> <time_settings> <name>
    challenge new GT0RL0PL2 19:19 F101 T1M3600O30P5S1B0D0 My Challenge

##### Responses
    