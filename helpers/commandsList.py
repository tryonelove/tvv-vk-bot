import commands

commands_list = [
    commands.staticCommands.HelpCommand,
    commands.funCommands.Roll,
    commands.funCommands.Weather,
    commands.funCommands.WeatherSet,
    commands.funCommands.Bitcoin,
    commands.osuCommands.OsuSet,
    commands.osuCommands.OsuPicture,
    commands.osuCommands.TaikoPicture,
    commands.osuCommands.ManiaPicture,
    commands.osuCommands.CtbPicture,
    commands.osuCommands.MatchmakingStats,
    commands.osuCommands.MatchmakingStatsDuo,
    commands.osuCommands.TopScoreCommand,
    commands.osuCommands.RecentScoreCommandOsu,
    commands.osuCommands.Compare,
    commands.levelCommands.GetLevel,
    commands.levelCommands.GetLeaderboard,
    commands.levelCommands.DisableLevels,
    commands.levelCommands.EnableLevels,
    commands.levelCommands.WipeLevels,
    commands.levelCommands.EditExperience,
    commands.donatorCommands.GetRole,
    commands.commandManager.AddCommand,
    commands.commandManager.DeleteCommand,
    commands.adminCommands.AddDonator,
    commands.adminCommands.RemoveDonator,
    commands.adminCommands.Op,
    commands.adminCommands.Deop,
    commands.adminCommands.Restrict,
    commands.adminCommands.Unrestrict,
    commands.adminCommands.AddRole,
]
