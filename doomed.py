import asyncio
import json
import random
import sys
import websockets

guesses = dict()
matched = []
known = [-1 for i in range(56)]
done = False

async def guess(websocket, x, y):
    msg = dict(op="guess", body=dict(x=x, y=y))
    await websocket.send(json.dumps(msg))
    response_str = await websocket.recv()
    response = json.loads(response_str)
    global done
    board = response["board"]
    done = response["done"]
    index = y * 7 + x
    value = board[index]
    known[index] = value
    print("%d, %d: " % (x, y), value)
    if value not in guesses:
        guesses[value] = [index]
    else:
        guesses[value].append(index)
    if "Flag" in response_str:
        print(response["message"])
        done = True
    return value

async def solve(uri):
    # Returns 403 if origin header not set.
    origin = "https://doomed.web.ctfcompetition.com"
    async with websockets.client.connect(uri, ssl=True, origin=origin) as websocket:
        msg = dict(op="info")
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        print(f"> {response}")
        dupes = dict()
        with open("dupes.txt") as f:
            for line in f:
                dupe = json.loads(line)
                key = "%d, %d, %d, %d" % (dupe[0], dupe[1], dupe[2], dupe[3])
                dupes[key] = dupe
        # Flip the first four cards.
        first = await guess(websocket, 0, 0)
        second = await guess(websocket, 1, 0)
        third = await guess(websocket, 2, 0)
        fourth = await guess(websocket, 3, 0)
        key = "%d, %d, %d, %d" % (first, second, third, fourth)
        if key in dupes:
            print("FOUND DUPE!")
            for index, value in enumerate(dupes[key][4:]):
                if value not in guesses:
                    guesses[value] = [index + 4]
                else:
                    guesses[value].append(index + 4)
        else:
            print("No match. Game over.")
            return

        while(not done):
            for value in guesses.keys():
                if len(guesses[value]) == 2 and value not in matched:
                    first_index = guesses[value][0]
                    first_x = first_index % 7
                    first_y = first_index // 7
                    first = await guess(websocket, first_x, first_y)
                    second_index = guesses[value][1]
                    second_x = second_index % 7
                    second_y = second_index // 7
                    second = await guess(websocket, second_x, second_y)
                    if first == second:
                        matched.append(value)
                        print("MATCHED: ", matched)
                    else:
                        print("MISS!!" , first, second)
                        print("Dupe doesn't match. Game over.")
                        return
            not_found = [i for i, val in enumerate(known) if val == -1]
            if not_found:
                next_guess = random.choice(not_found)
            else:
                return
            x = next_guess % 7
            y = next_guess // 7
            first = await guess(websocket, x, y)
            if len(guesses[first]) == 2:
                next_guess = guesses[first][0]
                matched.append(first)
            else:
                not_found = [i for i, val in enumerate(known) if val == -1 and i != next_guess]
                next_guess = known.index(-1)
                next_guess = random.choice(not_found)
            x = next_guess % 7
            y = next_guess // 7
            second = await guess(websocket, x, y)
            if first not in matched:
                if first == second:
                    matched.append(first)
            print("MATCHED: ", matched)

uri = "wss://doomed.web.ctfcompetition.com/ws"
asyncio.get_event_loop().run_until_complete(solve(uri))
