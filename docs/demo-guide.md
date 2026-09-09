# Demonstration walkthrough

Start with a fresh database or note that earlier actions persist. The included smoke script uses a separate disposable database, so it will not reset the normal demonstration.

1. Open the app and choose **S001 / Avery Tan**. Point out the initial 50 students and 10 courses.
2. Open **My profile**. Change the study goal or availability and save. Show the contact privacy hint and current-course selection. Keep the preferred course within the selected current courses.
3. Open **Find buddies**. Select IS442; try a study goal, meeting mode, and availability filter. Expand **Why this match?** on a result and explain how the five contributions add to the displayed score.
4. Open a result's study profile. Confirm the contact number is hidden. Send a request with a short message. Note the recipient's ID from the account selector/name; under the untouched defaults, Avery Lee is S021.
5. Switch to that recipient and open **Connections → Inbox**. Accept the request. Open **Active buddies → View profile & contact** and show the sender's contact number. Switch back to S001 and show the reciprocal access. End the connection and demonstrate privacy is restored. A separate request can demonstrate decline.
6. As S001, create an IS442 group with a name, description, goal, meeting mode, capacity, and one or more slots. Switch to S002 and request to join. Return to S001, open **Manage group**, and accept the membership request. Show removal or decline using a second student if desired.
7. In **Leadership handover**, pick an existing member. Explain that a leader cannot use ordinary member removal to quit. Demonstrate **Transfer & stay** or **Transfer & leave**. Switch to the replacement and show that they now manage the group. For a lone-leader example, create a separate group and use **Close group & leave**.
8. Choose **ADMIN001**. Show accounts, profile-completion status, usage, and last activity. Create a student account; select it and complete its profile. Return to admin to edit or suspend it. Delete only a deliberately created demonstration account after showing the confirmation.
9. Change the matching strategy or criterion weights and save. Return to S001 and run the same search; explain the changed scores. A zero weight disables that criterion; at least one criterion must remain positive.
10. Restart the backend, select a demo account again, and show that the saved data/configuration remain. Explain that sessions themselves are intentionally temporary.

## Suggested 12-minute presentation allocation

- 2 minutes: problem, actors, architecture and OOP responsibilities.
- 2 minutes: matching formula, availability calculation, strategy choices and trade-offs.
- 6 minutes: student, connections, groups, leader exit, and admin demonstration.
- 2 minutes: verification, limitations, actual team contributions, libraries, and AI-use disclosure.

Use the class diagram and component responsibilities in `architecture.md`. Fill in the team's real division of work and individual understanding; do not present generated implementation as evidence of each person's contribution. The final PPT and rehearsal remain team submission work, not completed application behavior.
