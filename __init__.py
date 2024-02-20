bl_info = {
    "name": "Simple Fade Manager",
    "author": "kanta",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "VSE(Sequencer) > Sidebar",
    "description": "BlenderのVSE(Video Sequence Editor)でフェード設定を簡単にするアドオン",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Sequencer",
}


def register():
    print(f"アドオン{bl_info['name']}が有効化されました")


def unregister():
    print(f"アドオン{bl_info['name']}が無効化されました")


if __name__ == "__main__":
    register()
