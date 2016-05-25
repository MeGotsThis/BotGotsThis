from ..library import feature, send

def commandFeature(args):
    return feature.botFeature(args.database, args.chat.channel, args.message,
                              send.channel(args.chat))
