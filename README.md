# Discord Bot for Travian

To help automate leadership tasks.

## How to use

* Required roles:
  * `Admin`: to create countdowns and create artifact rotations.
  * `def`: to be mentioned for countdowns.

### Commands

#### `!countdown`

* args:
  * `village-name`: name of village to defend. The created channel will be named countdown-`village_name`. If `village-name` contains spaces, The command will not work. Use hyphens to separate words.
  * `amount`: integer amount of the required troops. Must be a number.
  * `time`: expiration time of defense call.
  * `link`: link to village to defend

* Example: ```!countdown village-name 100000 00:00:00 <link>```

* Used to create countdowns for defense calls. This command will create the countdown channel within the category "countdown". If the category does not exist, it will be made.

* The purpose of this channel is to count down the number of troops being committed to a defense call until the countdown has reached 0. When the countdown reaches 0, the channel permissions will be adjusted and messages will no longer be able to be sent there. The channel will be automatically removed 24 hours after the countdown expires.

#### `!commit`

* args:
  * `amount`: integer amount of the number of troops being sent.

* Example: ```!commit 10000```

* User should `!commit` the exact number of troops sent. No abbreviations, such as 10k instead of 10000.

### Features still under development

* Artifact rotation manager:
  * Oversees artifact rotations for trainer and storage artifacts.

  * Users will be able to request artifacts and be added to wait-lists to use artifacts.
