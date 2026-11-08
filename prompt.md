# MiddleTV — Full UI, Native Apps, and System Integration Specification

You are working on MiddleTV, a fullscreen TV-style operating system and launcher built with Python and PySide6.

I want to expand MiddleTV into a complete TV-oriented operating system experience.

This is not just a launcher redesign. MiddleTV should provide a cohesive interface for media playback, applications, profiles, system settings, software installation, and system updates.

**Before making changes, inspect the entire existing repository. Understand the current architecture, features, dependencies, and UI switcher. Do not blindly rewrite the application.**

The screenshot provided in this conversation is the intended DEFAULT MiddleTV UI.

---

# 1. Default UI — Custom MiddleTV Interface

Reference: The latest screenshot provided.

This is the default interface I want users to see when they first install MiddleTV.

## Visual Design

The interface should have a futuristic, anime-inspired aesthetic.

The reference screenshot includes:

- A full-screen wallpaper.
- A custom MiddleTV OS label in the upper-left.
- A profile indicator in the upper-right.
- Large translucent dark application tiles.
- A blue outline around the focused tile.
- A futuristic, colorful background.
- A clean, fullscreen TV-oriented layout.

The wallpaper is an important part of the design.

The application tiles should remain readable over the wallpaper while allowing the background to show through.

Use translucent dark backgrounds rather than completely opaque cards.

The focused tile should have a noticeable blue outline.

The UI should be usable from a couch, with a keyboard, game controller, or TV remote.

## Home Screen Applications

The home screen should contain the following applications:

- About
- Settings
- Files
- Profiles
- Clock
- Jellyfin / Plex
- Flight Tracker
- YouTube
- Spotify
- Terminal

Use a responsive grid that adapts to the screen resolution.

Do not force every application into the same exact grid arrangement if doing so makes the screen awkward.

The home screen should feel like a dedicated TV interface rather than a conventional desktop.

---

# 2. UI Switcher

MiddleTV already has a UI switcher in Settings.

Preserve and improve the existing implementation.

The available UI styles should be:

- Modern, see [defaultUI.png](defaultUI.png)
- Aero, see [AeroTheme](aeroplane.jpg)
- Terminal, see [MatrixTheme](matrix.png)


The other UI styles should remain available.

Changing the selected UI should change the appearance of the application without breaking its functionality.

The selected interface should persist across restarts.

All supported applications should work regardless of which UI style is selected.

Do not create three separate versions of MiddleTV.

Use a shared application architecture with separate visual themes.

---

# 3. Native YouTube Application

Create a native MiddleTV YouTube application using the official YouTube APIs.

The application should be integrated into the MiddleTV launcher.

It should not simply open YouTube in an external browser.

## Features

Implement:

- YouTube search.
- Search results.
- Video thumbnails.
- Video titles.
- Channel names.
- Video descriptions.
- Video playback.
- Video information.
- Navigation between search results.
- Keyboard and remote control support.

The UI should be designed for a television.

Use large thumbnails and readable text.

The application should have a dedicated fullscreen player.

Use an appropriate playback backend, such as Qt Multimedia or another suitable supported player.

Do not assume that every YouTube URL can be played directly through a normal media player.

Use supported playback mechanisms and handle unavailable videos gracefully.

## API Configuration

The YouTube API key should be configurable in Settings.

The application should clearly indicate whether the API is configured.

Do not hardcode API keys into the source code.

Do not silently consume API quota through repeated unnecessary requests.

---

# 4. Dynamic Plex / Jellyfin Application

The home screen currently has a Jellyfin tile.

I want this to become a dynamic media-server tile.

The tile should automatically adapt to the configured media server.

## Behavior

If Jellyfin is configured:

- Display the Jellyfin application.
- Use Jellyfin branding where appropriate.
- Connect to the configured Jellyfin server.

If Plex is configured:

- Display the Plex application.
- Use Plex branding where appropriate.
- Connect to the configured Plex server.

If both are configured:

- Provide a sensible way to choose between them.
- Allow the user to configure which server appears as the primary home-screen tile.
- Do not silently discard either configuration.

If neither is configured:

- Display an appropriate setup prompt.
- Allow the user to configure a media server through Settings.

The media-server tile should not be hardcoded to Jellyfin.

## Native Application

Create a native MiddleTV application for the selected media server.

The application should provide:

- Server connection.
- Authentication.
- Library browsing.
- Movies.
- TV shows.
- Seasons and episodes.
- Media details.
- Playback.
- Resume playback where supported.
- Keyboard and remote navigation.

Use the appropriate Plex or Jellyfin APIs.

Preserve the existing media-server configuration if it already exists.

---

# 5. Native Spotify Application

Create a native Spotify application for MiddleTV.

The application should integrate with Spotify's supported APIs and authentication system.

## Features

Implement:

- Spotify authentication.
- Saved login/session handling.
- User's playlists.
- Saved albums.
- Saved tracks.
- Search.
- Playback controls.
- Playlist browsing.
- Album browsing.
- Track information.
- Keyboard and remote navigation.

The Spotify application should feel like a native MiddleTV application.

It should not simply open the Spotify website.

## Authentication

Use Spotify's supported OAuth authentication flow.

Persist authentication securely.

Do not store passwords or access tokens in plaintext.

Use an appropriate operating-system credential store where available.

Handle token expiration and refresh appropriately.

If Spotify requires an existing playback device or supported playback mechanism, communicate that clearly.

Do not assume that API access automatically provides unrestricted playback.

---

# 6. Global Escape / Back Navigation

I want MiddleTV to have consistent navigation across all applications.

Implement a shared navigation mechanism.

The goal is to make Escape, Back, and the appropriate remote-control button behave consistently.

## General Behavior

When the user presses Escape or Back:

1. If a dialog is open, close the dialog.
2. If a submenu is open, return to its parent menu.
3. If an application has an internal navigation stack, return to the previous screen.
4. If the user is at the application's root screen, return to the MiddleTV home screen.
5. If the user is already at the home screen, do not unexpectedly quit MiddleTV.

Do not make Escape immediately quit the entire operating system.

## Implementation

Use a shared navigation controller or Qt event-filter mechanism where appropriate.

Avoid adding separate, inconsistent Escape handlers to every widget.

The navigation system should respect the current application context.

Do not intercept Escape when the user is typing in a text field or when an application legitimately needs the key for another purpose.

Allow applications to define their own navigation behavior when necessary.

---

# 7. MiddleTV Startup and Session Management

MiddleTV should behave like a dedicated operating system.

When the application starts, it should perform an initialization sequence.

## Startup Sequence

1. Check whether MiddleTV is installed in the expected location.
2. Validate the application configuration.
3. Load the selected UI theme.
4. Load the configured user profile or profiles.
5. Restore the appropriate application settings.
6. Initialize the configured media servers.
7. Initialize supported integrations.
8. Display the MiddleTV home screen.

The startup sequence should be visible and understandable.

Use a MiddleTV-branded startup screen.

The startup screen can display progress messages such as:

- Initializing MiddleTV.
- Loading configuration.
- Loading profiles.
- Initializing applications.
- Starting MiddleTV.

Do not simulate progress that does not exist.

## Installation Verification

Check whether MiddleTV is installed and whether its required files are present.

If the installation is missing or incomplete, display an appropriate recovery/setup screen.

Do not silently attempt to install the application with elevated privileges every time it launches.

Installation and repair should be explicit operations.

## Profiles

Load the configured profile or profiles on startup.

Support:

- Default profile.
- Multiple user profiles.
- Profile-specific settings.
- Profile-specific application preferences.
- Profile selection.
- Profile switching.

Preserve the existing profile implementation if possible.

---

# 8. MiddleTV Settings — TV-Oriented System Settings

I want Settings to become a comprehensive system-management interface.

Think of KDE Plasma's System Settings, but redesigned for a television.

The interface should be fullscreen, readable from a distance, and usable with a remote.

Do not simply reproduce KDE's desktop interface.

Use MiddleTV's own visual identity.

## Settings Categories

Organize the settings into logical categories.

### Appearance

- UI theme.
- Wallpaper.
- Display settings.
- Focus appearance.
- UI scaling.
- Screensaver.
- Startup behavior.

### Profiles

- Manage profiles.
- Select profile.
- Create profile.
- Edit profile.
- Delete profile.
- Configure profile-specific applications.

### Media Servers

- Jellyfin configuration.
- Plex configuration.
- Server URL.
- Authentication.
- Connection testing.
- Primary media-server selection.

### Applications

- Installed applications.
- Application settings.
- Application installation.
- Application removal.
- Application updates.

### System

- System information.
- Operating system information.
- Hardware information.
- Network status.
- Storage information.
- System updates.
- Package management.
- System maintenance.

### Integrations

- YouTube API configuration.
- Spotify authentication.
- Other supported integrations.

### Notifications

- In-app notifications.
- Notification preferences.
- System notifications where supported.

## Settings UI

Use a consistent layout.

The settings should have:

- Clear category navigation.
- Readable headings.
- Consistent spacing.
- Properly aligned controls.
- Visible focus states.
- Clear status indicators.
- Contextual descriptions.

Avoid the current problem where every label is placed inside a bordered rectangle.

Do not make Settings look like a generic web form.

---

# 9. System Update GUI

Create a graphical interface for system updates.

The application should detect the operating system and its package manager.

Examples include:

- Fedora: DNF.
- Debian/Ubuntu: APT.
- Arch-based systems: Pacman, if supported.
- Other distributions: use the appropriate supported package manager.

Do not assume that every Linux system uses the same package manager.

## Features

The system update interface should provide:

- Check for updates.
- Display available updates.
- Show update progress.
- Display command output.
- Display errors.
- Report whether the update completed successfully.
- Allow the user to cancel when safe.
- Provide a reboot option when required.

The interface should be designed for a television.

Use readable progress indicators and clear status messages.

## Privileges

Package management may require administrator privileges.

Use the appropriate supported privilege-escalation mechanism for the operating system.

Do not automatically execute privileged commands without user authorization.

Before performing a system update, clearly explain that system packages will be modified.

Allow the user to confirm the operation.

Do not silently modify critical system files.

---

# 10. Application Installation GUI

Create a graphical application installer.

The goal is to allow users to install applications without needing to manually open a terminal.

The interface should support:

- Browse applications.
- Search applications.
- View application details.
- Install applications.
- Remove applications.
- View installation progress.
- Display errors.
- Display installed applications.

Where possible, use the operating system's supported package manager or software installation mechanism.

Do not assume that every application is available through every package manager.

Use a clear distinction between:

- Installed.
- Available.
- Installing.
- Updating.
- Failed.

The application installer should integrate into MiddleTV Settings.

---

# 11. MiddleTV Terminal

Create a native MiddleTV Terminal application.

This should be a GUI application that provides a terminal interface.

It should not simply be a settings page containing a few buttons.

The terminal should allow users to enter commands and view their output.

## Features

Implement:

- Command input.
- Command output.
- Scrollable output.
- Command history.
- Clear screen.
- Copy and paste.
- Keyboard navigation.
- Fullscreen operation.

The terminal should use a suitable shell for the operating system.

For Linux, use the user's configured shell where possible.

For Windows, use an appropriate supported shell.

The terminal should be usable with a keyboard.

## Safety and Privileges

Commands that modify the system should be handled carefully.

Do not automatically execute commands with administrator privileges.

When a command requires elevated privileges, use the appropriate authorization mechanism.

Provide a clear warning before destructive or system-critical operations.

The user should be able to understand what a command is going to do before authorizing it.

Do not silently execute arbitrary privileged commands in the background.

---

# 12. System-Wide Application Behavior

All MiddleTV applications should share a consistent application lifecycle.

Applications should:

- Open within the MiddleTV environment.
- Respect the selected UI theme where applicable.
- Support fullscreen operation.
- Support the shared Escape/Back navigation system.
- Respect profile settings.
- Handle errors gracefully.
- Return to the MiddleTV home screen appropriately.

Do not create a separate navigation system for every application.

Do not make every application independently manage the entire MiddleTV window.

Use a shared application framework.

---

# 13. Architecture and Implementation

Before implementing these features:

1. Inspect the repository.
2. Identify the main entry point.
3. Identify the current Settings implementation.
4. Identify the existing UI switcher.
5. Identify the profile system.
6. Identify the application launcher.
7. Identify existing media-server integrations.
8. Identify the current configuration storage.
9. Identify the existing navigation logic.
10. Identify the current packaging and installation process.

Reuse existing code wherever practical.

Do not introduce unnecessary dependencies.

Do not create duplicate implementations of existing functionality.

Do not rewrite the entire project just to add these features.

Use reusable components and a shared application architecture.

Keep the implementation modular.

If a feature cannot be implemented correctly because of API limitations, missing credentials, or operating-system restrictions, explain the limitation rather than creating a fake implementation.

---

# 14. Development Priorities

Implement this project incrementally.

Do not attempt to implement every feature in one enormous rewrite.

Recommended order:

1. Inspect the existing codebase.
2. Fix and polish the default MiddleTV UI.
3. Preserve and improve the UI switcher.
4. Implement shared navigation and Escape/Back behavior.
5. Improve startup and profile loading.
6. Implement the dynamic Plex/Jellyfin tile.
7. Implement the native media-server application.
8. Implement the native YouTube application.
9. Implement the native Spotify application.
10. Expand Settings into the TV-oriented system settings interface.
11. Implement system updates.
12. Implement the application installer.
13. Implement the MiddleTV Terminal.
14. Test all applications across the available UI themes.

After each stage, verify that existing functionality still works.

Do not mark a feature as complete until it has been implemented and tested.

## Final Objective

MiddleTV should feel like a complete, dedicated television operating system.

It should combine:

- A distinctive fullscreen interface.
- Multiple selectable UI themes.
- Native media applications.
- Profile management.
- Consistent navigation.
- System settings.
- Application installation.
- System updates.
- A native terminal.
- A cohesive application lifecycle.

The goal is a TV-oriented version of KDE Plasma's functionality, built around MiddleTV's own interface and application architecture.

The latest screenshot is the default UI reference.

The old smiley-face UI should not replace the new default.

Preserve the existing functionality and build on the current project rather than starting over.
