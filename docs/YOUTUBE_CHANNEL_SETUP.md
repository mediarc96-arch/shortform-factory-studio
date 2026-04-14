# YouTube Channel Setup

This guide is the recommended sequence for connecting a real YouTube channel to `Shortform Factory`.

Only `Channel Publisher & Analyst` should hold YouTube credentials.

## Required Values

You need these four values:

- `YOUTUBE_CHANNEL_ID`
- `YOUTUBE_OAUTH_CLIENT_ID`
- `YOUTUBE_OAUTH_CLIENT_SECRET`
- `YOUTUBE_OAUTH_REFRESH_TOKEN`

Recommended additional values:

- `YOUTUBE_DEFAULT_PRIVACY_STATUS=private`
- `YOUTUBE_DEFAULT_CATEGORY_ID=22`
- `YOUTUBE_DISCLOSURE_TEXT=AI로 만들어진 영상입니다.`
- `YOUTUBE_NOTIFY_SUBSCRIBERS=false`

## 1. Prepare Google Cloud

In Google Cloud Console:

1. Open the target project.
2. Enable `YouTube Data API v3`.
3. Create an OAuth client.
4. Use `Desktop app` as the client type.
5. Copy the client ID and client secret.

If the OAuth app is still in `Testing`:

1. Open the Google Auth/OAuth audience settings.
2. Add the real Google account you will log in with as a `Test user`.

## 2. Get The Channel ID

In YouTube:

1. Sign in as the real channel owner.
2. Open `Settings`.
3. Open `Advanced settings`.
4. Copy the channel ID.

Store that as `YOUTUBE_CHANNEL_ID`.

## 3. Get The Refresh Token

Run the OAuth helper on the Paperclip server:

```bash
cd /home/kindsr/paperclip
node scripts/youtube-oauth-bootstrap.mjs \
  --client-id "<YOUR_CLIENT_ID>" \
  --client-secret "<YOUR_CLIENT_SECRET>"
```

If your browser is on your local machine, use SSH port forwarding first:

```bash
ssh -L 8789:127.0.0.1:8789 kindsr@<paperclip-server>
```

Then:

1. Open the URL printed by the helper in your browser.
2. Log in with the actual YouTube channel owner Google account.
3. Approve access.
4. Wait for the helper to print:
   - `refreshToken`
   - `channelId`
   - `channelTitle`

Use:

- `refreshToken` -> `YOUTUBE_OAUTH_REFRESH_TOKEN`
- `channelId` -> `YOUTUBE_CHANNEL_ID` only if it is not `null`

If `channelId` is `null`, use the channel ID copied from YouTube settings instead.

## 4. Register Secrets In Paperclip

Company:

- `Shortform Factory`

Agent:

- `Channel Publisher & Analyst`

UI path:

1. Open `Shortform Factory`.
2. Open `Agents`.
3. Open `Channel Publisher & Analyst`.
4. Open `Configuration`.
5. Open `Permissions & Configuration`.
6. Find `Environment variables`.

Create rows for:

- `YOUTUBE_CHANNEL_ID`
- `YOUTUBE_OAUTH_CLIENT_ID`
- `YOUTUBE_OAUTH_CLIENT_SECRET`
- `YOUTUBE_OAUTH_REFRESH_TOKEN`

Then add:

- `YOUTUBE_DEFAULT_PRIVACY_STATUS`
- `YOUTUBE_DEFAULT_CATEGORY_ID`
- `YOUTUBE_DISCLOSURE_TEXT`
- `YOUTUBE_NOTIFY_SUBSCRIBERS`

For each sensitive value:

1. Enter it as `Plain`.
2. Click `Seal`.
3. Save it as a company secret.
4. Save the agent configuration.

## 5. Run A Manual Dry Run

Before letting the agent upload, verify directly:

```bash
cd /home/kindsr/paperclip
YOUTUBE_CHANNEL_ID="<channel-id>" \
YOUTUBE_OAUTH_CLIENT_ID="<client-id>" \
YOUTUBE_OAUTH_CLIENT_SECRET="<client-secret>" \
YOUTUBE_OAUTH_REFRESH_TOKEN="<refresh-token>" \
node scripts/youtube-upload.mjs \
  --title "Shortform Factory private test" \
  --description "Private test upload

AI로 만들어진 영상입니다." \
  --video-file "/absolute/path/to/test.mp4"
```

This validates the credentials and request shape without actually publishing.

## 6. Run A Private Test Upload

If the dry run is clean:

```bash
cd /home/kindsr/paperclip
YOUTUBE_CHANNEL_ID="<channel-id>" \
YOUTUBE_OAUTH_CLIENT_ID="<client-id>" \
YOUTUBE_OAUTH_CLIENT_SECRET="<client-secret>" \
YOUTUBE_OAUTH_REFRESH_TOKEN="<refresh-token>" \
node scripts/youtube-upload.mjs \
  --title "Shortform Factory private test" \
  --description "Private test upload

AI로 만들어진 영상입니다." \
  --video-file "/absolute/path/to/test.mp4" \
  --publish
```

Use `private` for the first upload test.

## 7. Agent-Driven Uploads

After credentials are set, `Channel Publisher & Analyst` can upload from a publish packet issue comment.

The comment must begin with:

```md
## YouTube Publish Packet Ready
```

Then include a JSON code block with the publish payload.

## Current Working Directory

The `Shortform Factory` agents are currently set to use:

- `/home/kindsr/projects/shortform-factory-studio`

That should be the canonical place for:

- episode packets
- renders
- thumbnails
- final video exports

## Guardrails

- Do not give YouTube secrets to `CEO`, `Head of Content`, `Script Writer`, or other creative agents.
- Keep the first test upload `private`.
- Include `AI로 만들어진 영상입니다.` in the YouTube description.
- If the OAuth app is still in testing mode, expect tester restrictions and possible token fragility.
