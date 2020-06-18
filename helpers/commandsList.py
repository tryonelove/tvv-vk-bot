import commands

commands_list = {
    "roll": commands.funCommands.Roll,
    "ролл": commands.funCommands.Roll,
    "weather": commands.funCommands.Weather,
    "погода": commands.funCommands.Weather,
    "osu": commands.osuCommands.OsuPicture,
    "taiko": commands.osuCommands.TaikoPicture,
    "mania": commands.osuCommands.ManiaPicture,
    "ctb": commands.osuCommands.CtbPicture,
    "level": commands.levelCommands.GetLevel,
    "lvl": commands.levelCommands.GetLevel,
    "лвл": commands.levelCommands.GetLevel,
    "leaderboard": commands.levelCommands.GetLeaderboard,
    "лидерборд": commands.levelCommands.GetLeaderboard,
    "addcom": commands.commandManager.AddCommand,
    "delcom": commands.commandManager.DeleteCommand,
    "role": commands.donatorCommands.GetRole,
    "add_donator": commands.donatorCommands.AddDonator,
}
