import wx


try:
    TESTING = False

    import eg

    Panel = eg.ConfigPanel
    try:
        Plugin = eg.PluginBase
    except ImportError:
        Plugin = object

    try:
        Action = eg.ActionBase
    except ImportError:
        Action = object

except ImportError:
    TESTING = True
    Panel = wx.Dialog
    Plugin = object
    Action = object



