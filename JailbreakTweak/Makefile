TARGET := iphone:clang:latest:15.0
INSTALL_TARGET_PROCESSES = SpringBoard
ARCHS = arm64 arm64e

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = NotiStarCloudTweak

NotiStarCloudTweak_FILES = Tweak.x
NotiStarCloudTweak_CFLAGS = -fobjc-arc
NotiStarCloudTweak_FRAMEWORKS = Foundation

include $(THEOS_MAKE_PATH)/tweak.mk
