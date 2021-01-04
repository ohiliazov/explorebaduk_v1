from typing import List


def make_pair(players, pairs, skipped_pairs: List[set]) -> set:
    paired = set.union(*pairs) if pairs else set()
    unpaired = [p for p in players if p not in paired]
    player, *opponents = unpaired

    for opponent in reversed(opponents):
        pair = {player, opponent}
        if pair not in skipped_pairs:
            return pair


def make_pairing(players, restricted_pairs):
    pairs = []
    skip_stack = [[]]
    unpaired = set(players)
    while skip_stack and len(unpaired) > 1:
        if pair := make_pair(players, pairs, restricted_pairs + skip_stack[-1]):
            pairs.append(pair)
            unpaired -= pair
            skip_stack.append([])
        elif pairs:
            last_pair = pairs.pop()
            unpaired |= last_pair
            skip_stack.pop()
            skip_stack[-1].append(last_pair)
        else:
            break

    return pairs


print(make_pairing(["player1", "player2", "player3", "player4", "player5", "player6", "player7", "player8"], []))
print(make_pairing(["player1", "player2", "player3", "player4", "player5", "player6", "player7"], []))
