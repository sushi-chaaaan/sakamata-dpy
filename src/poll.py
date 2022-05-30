import json

emoji = {
    "1": "\N{Large Red Circle}",
    "2": "\N{Large Green Circle}",
    "3": "\N{Large Orange Circle}",
    "4": "\N{Large Blue Circle}",
    "5": "\N{Large Brown Circle}",
    "6": "\N{Large Purple Circle}",
    "7": "\N{Large Red Square}",
    "8": "\N{Large Green Square}",
    "9": "\N{Large Orange Square}",
    "10": "\N{Large Blue Square}",
    "11": "\N{Large Brown Square}",
    "12": "\N{Large Purple Square}",
    "13": "\N{Large Orange Diamond}",
    "14": "\N{Large Blue Diamond}",
    "15": "\N{Heavy Black Heart}",
    "16": "\N{Green Heart}",
    "17": "\N{Orange Heart}",
    "18": "\N{Blue Heart}",
    "19": "\N{Brown Heart}",
    "20": "\N{Purple Heart}",
}

json.dump(emoji, open("emoji.json", "a"))

poll_emoji_list = []
