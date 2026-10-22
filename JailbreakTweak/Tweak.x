#import <Foundation/Foundation.h>

// Pre-configured Google Cloud Sync Constants
static NSString * const kDefaultDriveFolderID = @"1LoHXambgX8-b_mbUfBYHvYqQTZA6k0IU";
static NSString * const kDefaultWebAppURL     = @"https://script.google.com/macros/s/AKfycbzjPZ5K00RzxkpNRp_AMkq3FUrznjefkW-pq6cqlBzjeVuQ_Hp6YWeTiC9UvFqSy-r93w/exec";
static NSString * const kAppGroupSuite        = @"group.com.notistar.cloud.ios";

@interface BBBulletin : NSObject
@property (nonatomic, copy) NSString *bulletinID;
@property (nonatomic, copy) NSString *recordID;
@property (nonatomic, copy) NSString *publisherBulletinID;
@property (nonatomic, copy) NSString *sectionID;
@property (nonatomic, copy) NSString *title;
@property (nonatomic, copy) NSString *subtitle;
@property (nonatomic, copy) NSString *message;
@property (nonatomic, retain) NSDate *date;
@end

@interface BBServer : NSObject
- (void)publishBulletin:(BBBulletin *)bulletin destinations:(unsigned long long)destinations;
- (void)withdrawBulletinRequestsWithPublisherBulletinID:(NSString *)publisherID forSectionID:(NSString *)sectionID;
- (void)withdrawBulletinRequestsWithRecordID:(NSString *)recordID forSectionID:(NSString *)sectionID;
@end

static NSMutableDictionary<NSString *, NSDictionary *> *gCachedBulletins = nil;
static dispatch_queue_t gSyncQueue = nil;

static void NotiStarPostToGoogleCloud(NSDictionary *notiRecord) {
    if (!notiRecord) return;
    dispatch_async(gSyncQueue, ^{
        NSURL *url = [NSURL URLWithString:kDefaultWebAppURL];
        if (!url) return;

        NSMutableDictionary *payload = [NSMutableDictionary dictionaryWithDictionary:notiRecord];
        payload[@"action"] = @"sync";
        payload[@"sourcePlatform"] = @"iOS-Jailbreak-BBServer";
        payload[@"driveFolderId"] = kDefaultDriveFolderID;
        payload[@"folderId"] = kDefaultDriveFolderID;
        payload[@"notifications"] = @[notiRecord];
        payload[@"items"] = @[notiRecord];

        NSError *jsonErr = nil;
        NSData *bodyData = [NSJSONSerialization dataWithJSONObject:payload options:0 error:&jsonErr];
        if (!bodyData || jsonErr) return;

        NSMutableURLRequest *req = [NSMutableURLRequest requestWithURL:url];
        req.HTTPMethod = @"POST";
        req.timeoutInterval = 20.0;
        [req setValue:@"application/json; charset=utf-8" forHTTPHeaderField:@"Content-Type"];
        req.HTTPBody = bodyData;

        NSURLSessionDataTask *task = [[NSURLSession sharedSession] dataTaskWithRequest:req
                                                                     completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
            // Synced silently in background
        }];
        [task resume];
    });
}

static NSDictionary *NotiStarBuildRecordFromBulletin(BBBulletin *bulletin, BOOL isRevoked) {
    NSString *sectionID = bulletin.sectionID ?: @"com.apple.springboard";
    NSString *title = bulletin.title ?: sectionID;
    NSString *subtitle = bulletin.subtitle ?: @"";
    NSString *msg = bulletin.message ?: @"";
    if (msg.length == 0 && subtitle.length > 0) {
        msg = subtitle;
    }

    long long nowMs = (long long)([[NSDate date] timeIntervalSince1970] * 1000.0);
    NSDateFormatter *fmt = [[NSDateFormatter alloc] init];
    fmt.dateFormat = @"dd/MM/yyyy HH:mm:ss";
    NSString *dateStr = [fmt stringFromDate:[NSDate date]];

    NSString *pubID = bulletin.publisherBulletinID ?: (bulletin.recordID ?: (bulletin.bulletinID ?: [[NSUUID UUID] UUIDString]));
    NSString *uniqueKey = [NSString stringWithFormat:@"%@|%@", sectionID, pubID];

    return @{
        @"id": [NSString stringWithFormat:@"jb_%@_%lld", pubID, nowMs],
        @"key": uniqueKey,
        @"notificationId": @((int)(nowMs % 100000)),
        @"packageName": sectionID,
        @"appName": sectionID,
        @"title": title,
        @"contentText": msg,
        @"bigText": msg,
        @"inboxLines": @[msg],
        @"time": @(nowMs),
        @"dateStr": dateStr,
        @"isOngoing": @NO,
        @"hasRemoteInput": @YES,
        @"color": @(-16744193),
        @"isStarred": @(isRevoked),
        @"isSynced": @YES,
        @"isRevoked": @(isRevoked),
        @"cloudId": @"",
        @"smallIconB64": @"",
        @"largeIconB64": @"",
        @"pictureB64": @""
    };
}

%hook BBServer

- (void)publishBulletin:(BBBulletin *)bulletin destinations:(unsigned long long)destinations {
    %orig;

    if (!bulletin || !bulletin.message || bulletin.message.length == 0) {
        return;
    }

    NSDictionary *record = NotiStarBuildRecordFromBulletin(bulletin, NO);
    @synchronized(gCachedBulletins) {
        if (bulletin.publisherBulletinID.length > 0) {
            NSString *k1 = [NSString stringWithFormat:@"%@|%@", bulletin.sectionID ?: @"", bulletin.publisherBulletinID];
            gCachedBulletins[k1] = record;
        }
        if (bulletin.recordID.length > 0) {
            NSString *k2 = [NSString stringWithFormat:@"%@|%@", bulletin.sectionID ?: @"", bulletin.recordID];
            gCachedBulletins[k2] = record;
        }
    }

    NotiStarPostToGoogleCloud(record);
}

- (void)withdrawBulletinRequestsWithPublisherBulletinID:(NSString *)publisherID forSectionID:(NSString *)sectionID {
    if (publisherID.length > 0 && sectionID.length > 0) {
        NSString *lookupKey = [NSString stringWithFormat:@"%@|%@", sectionID, publisherID];
        NSDictionary *cached = nil;
        @synchronized(gCachedBulletins) {
            cached = gCachedBulletins[lookupKey];
        }
        if (cached) {
            NSMutableDictionary *revokedRecord = [cached mutableCopy];
            revokedRecord[@"isRevoked"] = @YES;
            revokedRecord[@"isStarred"] = @YES;
            NotiStarPostToGoogleCloud(revokedRecord);
            // Keep notification on lock screen instead of letting Zalo/Messenger wipe it!
            return;
        }
    }
    %orig;
}

- (void)withdrawBulletinRequestsWithRecordID:(NSString *)recordID forSectionID:(NSString *)sectionID {
    if (recordID.length > 0 && sectionID.length > 0) {
        NSString *lookupKey = [NSString stringWithFormat:@"%@|%@", sectionID, recordID];
        NSDictionary *cached = nil;
        @synchronized(gCachedBulletins) {
            cached = gCachedBulletins[lookupKey];
        }
        if (cached) {
            NSMutableDictionary *revokedRecord = [cached mutableCopy];
            revokedRecord[@"isRevoked"] = @YES;
            revokedRecord[@"isStarred"] = @YES;
            NotiStarPostToGoogleCloud(revokedRecord);
            return;
        }
    }
    %orig;
}

%end

%ctor {
    gCachedBulletins = [NSMutableDictionary new];
    gSyncQueue = dispatch_queue_create("com.notistar.cloud.ios.jbqueue", DISPATCH_QUEUE_SERIAL);
}
