# casestudy

This repository contains results to case study assignment.

As a first step run below command in your terminal to install all requirements.

```codebloack
pip install -r requiremnts.txt
```

1. The questions from 1 to 8 are answered in `case_study_results.ipynb`
2. The question 9 is answered in `automated_task.py` but to run it as an
    automated scheduled job, the script in `scheduler.py` needs to be executed.
3. Run `scheduler.py` as background process with below command
```codeblock
nohup python scheduler.py &
```

**Note** : In `automated_task.py`, the email and password of the sender 
needs to be set. For gmails to work, you need to enable app password.
1. Go to your Google Account.
2. Select Security.
3. Under "Signing in to Google," select App Passwords. You may need to sign in. If you don’t have this option, it might be because:
    * 2-Step Verification is not set up for your account.
     * 2-Step Verification is only set up for security keys.
     * Your account is through work, school, or other organization.
     * You turned on Advanced Protection.
8. At the bottom, choose Select app and choose the app you using and then Select device and choose the device you’re using and then Generate.
9. Follow the instructions to enter the App Password. The App Password is the 16-character code in the yellow bar on your device.
10. Tap Done.

**Note** : Setup your api-key to access the Guardian APIs and replaces the
values in the app.