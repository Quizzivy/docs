# F2 — Messaging: any student, and colleagues (v0.15.x)

A release outside the train, asked for by the owner. It widens R7's Messages (`77-r7.md`, D17) in
three ways. **Staff write to any student:** every staff member who opens the teacher workspace,
teachers and admins alike, may start a direct thread with any enabled student, in a class or in
none. **Students keep R7's rule for writing first:** only to the teacher of a class they are in
now that is not archived, and they reply in any thread a staff member started. **Colleagues
write to each other:** direct threads between two staff members, with files, unread counts,
in-app items and email, as a staff member's thread with a student has.

The owner's words (2026-11-23), after finding on production that the Admin could not write to a
student of a teacher's class and that nobody could write to a student in no class: "không chỉ
admin mà giáo viên có thể nhắn cho bất cứ học viên nào. Chỉ có học viên là chỉ nhắn được cho giáo
viên của mình thôi." He also asked for chat between teachers, "thuận lợi cho việc share tài liệu
và trao đổi kinh nghiệm". The questions below are his to answer, each with the default this file
and the F2 proposal page are drawn at (Quizzivy/web#157).

It runs like F1 (`77f-f1-assignment-modes.md`): tasks `T-F2.<n>`, branches
`feature/t-f2-<nn>-<slug>` off the integration branch `work/messaging-f2`. The build starts once
R8's contract (T-R8.1, Quizzivy/sdk) is on `develop`, so the two contract steps never sit side by
side unmerged, and F2 is released after R8 (v0.15.0) as the first patch free after it: the contract
change is additive (below), so the SDK gate asks for no new minor (D-080). R8 is not touched and
does not grow. Where F2 meets R8's files it is named under "R8 and F2" below.

**Deliverable:**

- Staff Messages finds any enabled student. The list's search returns students beyond the
  caller's classes, and a **New message** button opens a picker of students (filtered by all, the
  caller's classes, one of them, or in no class) and of colleagues. A student row shows the
  student's current classes, or "In no class".
- The Students page and class detail offer Send message for every enabled student they list
  (`canMessage`), not only the caller's own.
- A student reads a thread a staff member who does not teach them started, sees that staff
  member as "Teacher at the centre", and replies to it. A student still writes first only to a
  teacher of a current class.
- A **Colleagues** tab in staff Messages, and colleague threads in All: one thread per pair of
  staff members, either side may attach a file (the R7 types and size), unread counts in the
  sidebar and the bell, in-app items and emails under the "New message" switch.
- Every existing thread reads and behaves as before; a former student is still "Former student".

**Exit criteria:**

- The five canaries pass untouched.
- `make sdk-check` passes without the `contract-breaking` label.
- The isolation suite gains every new operation, and its DM cases still pass: teachers A and B
  and an Admin each read only their own thread with a student, and C reads only C's own thread
  with A, never A's thread with B.
- `permissions.golden` gains the new operations and changes nothing else.
- The migrations pass goose up/down/up and are rehearsed on a copy of the production database. A
  v0.15.0 pod keeps reading and writing conversations during the rolling deploy and never sees a
  colleague thread.
- The staff list, the picker, both threads and the student's Messages match the F2 proposal page
  (T-F2.0) at 360, 768, 1024, 1280 and 1440, light and dark, every departure a row in
  `docs/design/gaps.md`.
- Every CI step of `70-redesign-overview.md` §8 is green on the release pull request,
  `pnpm e2e:live` included.

**Depends on:** v0.15.0 (R8) released, or at least R8's contract on `develop` for the build to
start (Order of work). F2 builds on R7's messaging module and screens (T-R7.9 to T-R7.12, T-R7.20,
T-R7.21), R7's email channel (T-R7.13) and R4's notifications and summaries.

## What exists (develop, 2026-11-23)

Read from `develop` of every repository on 2026-11-23 (api at v0.14.1 plus its back-merge). The
names are the code's; line numbers are left out because they drift.

- **The staff rule.** `messaging/domain/eligibility.go`: `Peer` is a thread between the two, a tie
  (`app.messaging_ties`) or the staff member having created the account (and it being a
  student); `PostDirect` adds an enabled account that still passes the student predicate.
  `scope.all` widens none of it. The same rule is written once in SQL,
  `shared/visibility/messaging.go` (`MessagingPeerIDs`, `CanMessage`), which
  `messaging/repositories/eligibility.go` (`directFactsSQL`), the list's candidates
  (`repositories/threads.go`, `candidateRows`), `StudentRow.canMessage` and
  `ClassMember.canMessage` read.
- **The path kind.** `{studentId}` on the three staff direct operations declares `x-resource`
  kind `messaging-peer` ("a student a staff member may read a direct thread with", the contract's
  kind list), and the isolation world resolves it to the other teacher's student
  (`server/tests/isolation_world_test.go`), so today another teacher's student answers 404.
- **The student rule.** `messaging/domain/student.go`: `Teacher` is a thread that exists, whoever
  wrote first, or the teacher of a class the student is in now that is not archived;
  `PostAsStudent` adds an enabled staff account. **So a student already replies in a thread any
  staff member started.** The list and the header read `classNames` and `former`; with neither,
  the web writes "Your teacher" alone (spec §9, written for the account's creator).
- **The ties.** `app.messaging_ties` (`00167`) remembers who has taught whom, written by
  `shared/ties` in every enrolment and change of teacher and filled at migration. It decides
  `Tied` in the staff rule and `former` on both sides (`threads.go`, `former`;
  `repositories/student.go`, `formerTeacher`); D16's anonymisation deletes an account's rows
  (`core/maintenance/anonymize.go`, `forgetTies`). `00167` also added two deferred fill triggers
  for the R6 binary during R7's rolling deploy, and its comment, and `00169`'s, say "R8's contract
  step drops both triggers and their functions". `78-r8.md` as merged does not list the drop,
  but R8's T-R8.2 builds it on `work/redesign-r8` (the hosting session, 2026-11-23), so it is R8's
  and F2 leaves it there.
- **The data model.** `app.conversations` (`00164`) is `kind IN ('class','direct')` with
  `class_id`, or `staff_id` plus `student_id`, each shape held by a CHECK; one direct thread per
  `(staff_id, student_id)`; RESTRICT keys to users and classes. `messages`, `conversation_reads`
  and `message_attachments` name only a conversation and users, so they hold a thread of any
  kind as they are.
- **Files.** `messaging/application/command/upload_attachment.go` and `platform/filetype`:
  PDF, DOCX, DOC (macros refused), PNG, JPEG (10000 × 10000 cap), MP3, M4A, 20 MiB; uploads are
  staff only (`/teacher/messages/attachments`), and a download is open to the uploader before
  sending and to the participants of the thread that holds it
  (`repositories/attachments.go`).
- **Notices and counts.** `domain/notice.go`: a staff reader's `message.received` item leads to
  `StudentID`'s thread (`NotificationTarget.route: messages` with `studentId`); a student's
  `message.from_teacher` to `TeacherID`'s thread. `StaffUnread` and `StudentUnread`
  (`repositories/notices.go`) sum direct threads by `staff_id` or `student_id` and channels by
  scope. The email `message_received` names the sender and the class, never the body, waits ten
  minutes and goes at most once per thread per 30 minutes (T-R7.13).
- **Colleagues are listed already, for sharing.** `searchTeacherDirectory`
  (`/teacher/directory/teachers`, `content.share`) lists accounts that open the teacher workspace
  (`limits.TeacherRole`), active or disabled, never the caller, never an anonymised account, with
  name, display name, **email** and photo: the 77-r7 leak note says a colleague's name and email
  reach holders of `content.share` by design. The built-in teacher role holds `content.share`
  (`00054`); a custom staff role may open the workspace without it.
- **The web.** `web/src/features/messages/`: `TeacherMessagesPage.tsx` with `ThreadList.tsx` (tabs
  All, Classes, Direct; a search that also lists `candidate` rows under "Học viên chưa nhắn tin"),
  `ThreadView.tsx`, `ThreadDetails.tsx`, `Composer.tsx`, `AttachDialog.tsx`; the student's
  `StudentMessagesPage.tsx`. There is no New message button: a teacher starts a thread from the
  search, Students, or class detail.
- **The deck.** `R7 Messages.dc.html` (DG-91) draws the list, both threads, the search's
  candidates, Details and the student's Messages; nothing draws a picker, a staff-to-staff thread
  or a staff member who never taught the student.

## Decisions taken in this file

- **The ties stay; only the staff rule stops reading them.** A tie still tells "Former student"
  and "Former teacher" apart from a student the caller never taught, which the deck draws. So
  `app.messaging_ties`, `shared/ties` and anonymisation's `forgetTies` stay as they are, and
  `Tied` leaves `DirectFacts`. Dropping the table would lose the labels and gain nothing.
- **R8 drops 00167's fill triggers, not F2.** They served the R6 binary during R7's rolling
  deploy; the R7 binary writes every tie itself (`shared/ties`). R8's T-R8.2 drops them, as
  `00167` says, and F2's migration assumes they are gone. If R8 ships without the drop, F2's
  migration adds it (`DROP … IF EXISTS`), never both.
- **The staff rule becomes "a thread, or a student".** `Peer` is a thread between the two, or an
  account that passes R2's strict student predicate (`app.student_like_roles`) and is not
  anonymised; `PostDirect` keeps "enabled and still a student". `scope.all` plays no part:
  every staff member who opens the workspace gets the same rule, so the Admin gains nothing a
  teacher lacks. `Created` leaves the rule, since a student the caller created is a student.
- **A thread stays its two participants'.** Widening who may start a thread does not widen who
  reads one: a direct thread is addressed by its counterpart (`students/{studentId}`), so teacher
  B naming student S reads B's thread with S, never A's (D17, DG-08). Nothing in F2 opens a
  thread to a third person, the Admin included.
- **Reaching a student to message them is not R2 reach.** Messaging any student opens no profile,
  result, attempt or class of theirs. `student` keeps R2's scope; the password and email rule of
  T-R2.13 (`STUDENT_SHARED`) is unchanged, because a thread is opened by being its participant,
  never by an account change.
- **The picker shows the student's class names, nothing more.** Name, photo, and the names of the
  student's current classes that are not archived (the caller's own first), or "In no class": two
  students with one name must be told apart, and in a one-centre organisation the class names are
  the least that does it. No email, username, teacher name, member count or result. The same
  names are the sub-line of a thread with a student the caller does not teach, as a new field
  (`otherClassNames`), names only, never a link out of the caller's class scope.
- **A colleague thread is its own kind, with its own pair of columns.** `conversations` gains
  `kind = 'colleague'` with `colleague_low_id` and `colleague_high_id` (the two staff accounts,
  the smaller uuid first, `CHECK (low < high)`), one thread per pair. Putting two staff members in
  `staff_id` and `student_id` would make every query that reads `student_id` (the student's list,
  unread, notices, anonymisation, the export) wrong for them. A members table would allow groups,
  which Q7 defers; a group release would add it then.
- **Colleague threads have their own operations, so the contract stays additive.** A new value of
  `StaffThreadRef.kind` would be a response enum widened, which is breaking (the SDK README), and
  an old tab would meet a row it cannot open. So colleagues are under
  `/teacher/messages/colleagues`: their list, a thread, its post and its read pointer, and the
  web shows them in All by merging the two lists, newest first. `NotificationTarget` gains an
  optional `colleagueId`, a new property of a response object, which is additive.
- **One finder for both pickers.** `GET /teacher/messages/recipients` lists students or colleagues
  to write to, browsable without a query, filtered for students by the caller's classes or by
  "in no class", paged. It is not a list of owned resources, so its rows are under `recipients`,
  as `searchTeacherDirectory`'s are under `teachers`, and it declares no `x-resource-list`.
- **A colleague is an account that opens the teacher workspace.** Enabled, not the caller, not a
  student, not anonymised (`limits.TeacherRole`, as the share directory reads it); a disabled
  colleague with a thread keeps it readable and takes no post, as a disabled student does. An
  account that opens only the Admin console is not one: it cannot open Messages.
- **The colleague directory shows no email.** Messaging is open to every holder of
  `workspace.teacher`, a wider set than `content.share` can be, so it shows a colleague's name,
  photo and role name only.
- **Files, rate limits and email are R7's, unchanged.** Both sides of a colleague thread are
  staff, so both may attach, through the same upload, types, size and sniffing. A colleague post
  has its own limiter entries at the staff post's numbers (30 a minute, 500 a day). Its email is
  `message.received` under the teacher's "New message" switch, with the same wait and dedupe, and
  names no class. No `NotificationKind` and no `NotificationEvent` value is added.
- **No attempt cards, no "Seen by" between colleagues.** A colleague thread's response is its own
  schema without `contextEvents` or `seenBy`.
- **Not audited, as R7.** Colleague posts, reads and uploads write no audit row; `messages` is
  the record (O-R7.6).

## R8 and F2

- **Migrations.** R8's files (T-R8.2: `00175` to `00178` on `work/redesign-r8` on 2026-11-23,
  plus the trigger drop) and F2's one are numbered in the order they reach `develop`: R8's first.
  F2 writes its file as `NNNNN_…` on its branches and numbers it when `work/messaging-f2` is
  merged with `develop` after R8, so goose never meets an F2 file below an applied R8 one.
- **The triggers.** R8's T-R8.2 drops them (above). F2's T-F2.2 reads R8's file before it is
  written and adds nothing on the triggers unless R8 ships without the drop.
- **The contract.** R8's contract is on sdk `develop` since 2026-11-23 (Quizzivy/sdk#35,
  `contract-breaking`, published as `0.14.2-dev.202611230156.g512db48`). F2's sdk pull request is
  cut from that `develop` and merges after R8's sdk release is cut (`release/0.15.0`), so
  v0.15.0 carries no F2 operation the R8 API does not implement. Until then the F2 api and web
  branches build on that pull request's tree locally, as R8 did with `sdk-r8-pin1`.
- **Shared files.** F2 touches `identity/repositories/delete.go` and
  `classes/repositories/delete.go` only through the constraint-name map that T-R8.2 also edits
  (`referencedBy: attendance`); F2's entries are added after R8's are on `develop`.

## A. Design

### T-F2.0 — Proposal page and the design row
**Depends on:** —
**Touches (Quizzivy/web):** `docs/design/deck/proposals/F2 Messaging.dc.html`,
`docs/design/deck/MANIFEST.sha256`, `docs/design/deck/README.md` (Log), `docs/design/gaps.md`
(DG-233)
**Size:** M
**Done when:**
- [ ] The page follows the proposal layout (cover, decisions, frames at 1280 and 360 in light and
      dark, state table, copy vi/en, open questions, handoff), with `R7 Messages.dc.html`'s own
      list, thread and student frames set beside the new ones.
- [ ] It draws: the list with New message and the Colleagues tab; the picker's students and
      colleagues, with its filter, a search, a row that already has a thread, no match, loading
      and error; the list's search finding students beyond the caller's classes and colleagues;
      a thread with a student the caller does not teach and its Details; a colleague thread
      (empty, normal with files from both sides, disabled account, Details); the student's view of
      a thread a staff member who does not teach them started.
- [ ] DG-233 is added to `gaps.md` and names the page; `node scripts/check-design-deck.mjs` passes
      with the regenerated manifest.
- [ ] A design issue in `Quizzivy/web` with Plan ID DG-233 on the board, and the page published to
      the "Quizzivy mockups" canvas. Its questions are this file's Q1 to Q13, on one "questions
      for the owner" issue for F2.

## B. Contract and server

### T-F2.1 — Contract: any student, recipients, colleague threads
**Depends on:** R8's contract on sdk `develop` (Quizzivy/sdk#35, merged 2026-11-23)
**Touches (Quizzivy/sdk):** `api/openapi.yaml`, `sdk/`
**Size:** M
**Done when:**
- [ ] The `messaging-peer` kind's description reads "a student a staff member may read a direct
      thread with: one they have a thread with, or any account that passes the student
      predicate"; `getStaffDirectThread`, `postStaffDirectMessage` and
      `markStaffDirectThreadRead` say any enabled student may be written to, and
      `StudentRow.canMessage` / `ClassMember.canMessage` say the same.
- [ ] `StaffThread` and the direct thread's peer gain `otherClassNames` (array of strings, names
      only): the student's current classes that are not archived and that the caller does not
      teach. Required in the response; additive.
- [ ] `GET /teacher/messages/recipients` (`listMessageRecipients`, `workspace.teacher`): query
      `audience` (`students` | `colleagues`, required), `q` (≤ 200), `classId` (a class in the
      caller's scope, `x-resource` kind `class`) or `inNoClass` (boolean), `cursor`, `limit`
      (1–50, default 30). Answers `{recipients: [MessageRecipient], nextCursor}`.
      `MessageRecipient {id, name, avatarUrl, classNames, otherClassNames, roleName, threadExists, canPost}`:
      `classNames` the caller's classes the student is in, `otherClassNames` the rest, both empty
      for a colleague; `roleName` the colleague's role, `null` for a student. Limited to 60 a
      minute per signed-in user. Its description carries the leak review (T-F2.7).
- [ ] `GET /teacher/messages/colleagues` (`listColleagueThreads`, `workspace.teacher`, `?q=`):
      `{items: [ColleagueThread]}`, where `ColleagueThread {colleagueId, title, avatarUrl, roleName, candidate, disabled, lastMessageAt, preview, unread}`;
      with `q`, after the threads, up to 20 colleagues with no thread as `candidate: true`.
- [ ] `GET /teacher/messages/colleagues/{colleagueId}` (`getColleagueThread`), `POST` on the same
      path (`postColleagueMessage`, `{clientId, body?, attachmentId?}`, 201 or 200 on a repeated
      `clientId`) and `POST …/{colleagueId}/read` (`markColleagueThreadRead`), all
      `workspace.teacher`. `{colleagueId}` declares a new `x-resource` kind
      `messaging-colleague`; body `/attachmentId` declares `attachment`. The thread is
      `ColleagueDirectThread {colleague: {id, name, avatarUrl, roleName, disabled, canPost}, items: [StaffMessage], nextBefore, latestId}`,
      with no `contextEvents`; a post to a disabled colleague answers 409
      `MESSAGING_NOT_ALLOWED`.
- [ ] `NotificationTarget` gains `colleagueId` (optional), present on a `message.received` item
      for a colleague thread; the kinds table says a colleague's item carries no `className`.
- [ ] The upload and staff download describe the colleague thread as a place a file is sent.
- [ ] No enum gains a value. `make gen` is its own commit; `make sdk-check` passes without
      `contract-breaking`.
- [ ] The api pull request on this contract (T-F2.2 onward) is green before this one merges
      (D-082 (iii)).

### T-F2.2 — Migration: colleague conversations
**Depends on:** T-F2.1
**Touches (Quizzivy/api):** `migrations/NNNNN_colleague_conversations.sql`,
`server/internal/platform/db/tests/{constraints,privileges,migrate}_test.go`,
`server/internal/modules/identity/repositories/delete.go` (T-R2.13's map) and its integration
test, `docs/plan/20-data-model.md`
**Size:** M
**Done when:**
- [ ] It is numbered after R8's migrations, and R8's trigger drop is on `develop` first (R8 and
      F2, above); a test enrols a student through the module and finds the tie, so `shared/ties`
      alone still writes them.
- [ ] `colleague_conversations`:
      - `conversations_kind_check` becomes `kind IN ('class', 'direct', 'colleague')`, added
        `NOT VALID` and validated in the same file.
      - `colleague_low_id` and `colleague_high_id`, `uuid NULL REFERENCES app.users(id) ON DELETE
        RESTRICT`.
      - `conversations_colleague_shape`: `kind <> 'colleague' OR (class_id IS NULL AND staff_id
        IS NULL AND student_id IS NULL AND colleague_low_id IS NOT NULL AND colleague_high_id IS
        NOT NULL AND colleague_low_id < colleague_high_id)`; `conversations_colleague_columns`:
        `kind = 'colleague' OR (colleague_low_id IS NULL AND colleague_high_id IS NULL)`. Both
        `NOT VALID`, then validated: every existing row has the two columns null.
      - A unique index on `(colleague_low_id, colleague_high_id) WHERE kind = 'colleague'`, and
        one on each column with `last_message_at DESC` under the same predicate, each side's list.
        The table is small (one row per thread), so no `CONCURRENTLY`.
      - The app role's UPDATE stays on `last_message_at` alone; `quizzivy_maintenance` gains
        `SELECT (colleague_low_id, colleague_high_id)`, for anonymisation.
      - Down refuses while a colleague conversation exists (the v0.15.0 binary cannot read one,
        as `00174`'s Down refuses for a flexible assignment), then drops the indexes, the checks
        and the columns and restores the two-kind check.
- [ ] The new keys join T-R2.13's map in `identity/repositories/delete.go`:
      `conversations_colleague_low_id_fkey` and `conversations_colleague_high_id_fkey` answer
      `referencedBy: messages`; an integration test deletes a teacher with a colleague thread and
      gets 409, never a 500.
- [ ] `constraints_test.go` covers both checks and the unique index (a pair written high-first
      is refused; a second thread for a pair is refused); `privileges_test.go` the maintenance
      grant. goose up/down/up passes, and an integration test inserts a direct thread and a class
      channel the v0.15.0 way (no new column named).
- [ ] `20-data-model.md` gains the section and its D-row (T-F2.10).

### T-F2.3 — Staff to any student
**Depends on:** T-F2.2
**Touches (Quizzivy/api):** `messaging/domain/{eligibility,thread}.go`,
`messaging/repositories/{eligibility,threads}.go`, `shared/visibility/messaging.go`,
`messaging/http/staff.go`, the `messaging-peer` resolver, `server/tests/isolation_*_test.go`,
the Students and class-roster reads that carry `canMessage`
**Size:** M
**Done when:**
- [ ] `Eligibility.Peer` is "a thread, or a student, never yourself": `DirectFacts` loses `Tied`
      and `Created`; `PostDirect` still needs the account enabled and a student. The table test
      covers: another teacher's student, a student in no class, a disabled student (readable when
      a thread exists, 404 without one, 409 on a post), a staff account (404 without a thread),
      an anonymised account (404), yourself (404).
- [ ] `MessagingPeerIDs` and `CanMessage` say the same in SQL, once, and `StudentRow.canMessage`
      and `ClassMember.canMessage` read it; an anonymised account is never a peer.
- [ ] The list's search returns, after the threads, up to 20 enabled students with no thread whose
      names, or whose current class names, match; `former` is as today; `otherClassNames` is
      filled on every direct row and candidate.
- [ ] `listMessageRecipients` for `students`: enabled students by name (accent-insensitive, the
      query as the share directory's), the caller's classes first in `classNames`, filtered by
      `classId` (one of the caller's classes; another's answers 404 by `x-resource`) or
      `inNoClass`; keyset-paged by folded name and id; `threadExists` and `canPost` per row.
- [ ] The isolation suite: `messaging-peer` no longer follows the other teacher's scope, so the
      suite's table records it as an exemption with the reason ("any student may be written to;
      the thread read is the caller's own"), and explicit cases hold D17: teachers A and B each
      write to student S, and A's read returns only A's messages, B's only B's, and the Admin's
      read of S returns the Admin's own empty thread.
- [ ] Context events in a thread with a student the reader does not teach are the reader's
      assignment scope as today, so none appear; a test pins it.

### T-F2.4 — Colleague threads
**Depends on:** T-F2.2
**Touches (Quizzivy/api):** `messaging/domain/{thread,eligibility,notice,colleague}.go`,
`messaging/application/{command/{post_colleague,mark_read_colleague}.go,query/{colleague_threads,colleague_messages,recipients}.go,ports/ports.go}`,
`messaging/repositories/{colleagues,messages,reads,notices,attachments}.go`,
`messaging/http/{staff,colleagues}.go`, `core/router/{server.go,ratelimits.go}`, the
`messaging-colleague` resolver, `server/tests/isolation_*_test.go`
**Size:** L
**Done when:**
- [ ] `ColleagueFacts` and `Eligibility.Colleague`: a thread between the two, or an account that
      opens the teacher workspace and is not a student, not anonymised and not yourself; a post
      also needs it enabled. The table test covers a teacher, an Admin, a custom staff role with
      the workspace, a role with only the Admin console (404), a student (404), a disabled
      colleague (readable with a thread, 409 on a post), yourself (404).
- [ ] The first post creates the conversation with the pair ordered low-first
      (`INSERT … ON CONFLICT DO NOTHING` on the partial unique index), locks it before the
      message id is made as R7's posts do, and bumps `last_message_at`; a repeated `clientId`
      answers 200 with the existing message.
- [ ] `listColleagueThreads` and `getColleagueThread` read only threads where the caller is one of
      the pair; `listMessageRecipients` for `colleagues` lists colleagues by name with
      `threadExists`.
- [ ] A file is sent in a colleague thread exactly as in a student's; the download admits the
      two colleagues and the uploader before sending, and answers 404 to anyone else, an Admin
      included.
- [ ] `StaffUnread` (`/teacher/summary.unreadMessages`) adds the colleague threads past the
      caller's pointer, never their own messages.
- [ ] `message.received` for a colleague thread: one item per reader per thread, upserted while
      unread, its target `{route: messages, colleagueId}`, honouring the reader's in-app switch;
      the email under the same switch, wait and dedupe as a student's thread, naming the sender
      and no class.
- [ ] Rate limits: colleague posts at 30 a minute and 500 a day per staff user, reads and the
      recipients list at 60 a minute, in `PrincipalRateLimits()`.
- [ ] Every new operation joins the isolation suite: `{colleagueId}` resolves a colleague;
      teachers A, B and C with A↔B a thread: C naming A reads C's own (empty) thread, never A↔B;
      the Admin naming A reads the Admin's own; a student session under `/teacher` is refused by
      audience. `/clientId` and `/lastReadMessageId` are recorded as exemptions as in R7.
- [ ] Posts, reads and uploads write no audit row.

### T-F2.5 — Export, anonymisation and deletes
**Depends on:** T-F2.2
**Touches (Quizzivy/api):** R5's export worker (`messages_summary.csv`) and its `README.txt`,
`core/maintenance/anonymize.go`, `core/maintenance/tests/retention_test.go`,
`exports/repositories/tests/source_messages_test.go`
**Size:** S
**Done when:**
- [ ] `messages_summary.csv` writes a colleague thread as kind `colleague` with its two
      participant ids, the count and the dates; still no body, filename or attachment. The
      `README.txt` says so in vi and en.
- [ ] D16's anonymisation deletes a disabled account's colleague threads with their messages,
      reads and attachment rows, in the same transaction as its direct threads; their objects go
      in the housekeeping sweep as R7's do. A teacher who owns content is still skipped (R5), so
      in practice it removes the threads of a teacher with no content. A test covers it.

## C. The web

### T-F2.6 — Staff: any student, the picker
**Depends on:** T-F2.0, T-F2.1
**Touches (Quizzivy/web):** `web/src/features/messages/{api.ts,entry.ts,links.ts}`,
`components/{ThreadList,ThreadDetails,ThreadView}.tsx`, a new `components/RecipientPicker.tsx`,
`pages/teacher/TeacherMessagesPage.tsx`, `lib/i18n/locales/{vi,en}/teacher.json`
**Size:** M
**Done when:**
- [ ] New message at the list's head opens the picker as on the F2 page: students and colleagues,
      the search, the students' filter (all, the caller's classes, one class, in no class), paged
      on scroll; a row with a thread opens it, any other row opens the empty thread with the
      composer focused.
- [ ] The search's candidates and a direct row's sub-line show the caller's classes, else
      `otherClassNames`, else "In no class", and "Former student" as today.
- [ ] Details for a student the caller does not teach says so in one sentence and links nothing
      out of scope.
- [ ] Vietnamese is written first, and the pull request lists every new key.

### T-F2.7 — Staff: colleague threads
**Depends on:** T-F2.0, T-F2.1
**Touches (Quizzivy/web):** `web/src/features/messages/{api.ts,links.ts,stream.ts,useThread.ts}`,
`components/{ThreadList,ThreadView,ThreadDetails,Composer,StaffAttach}.tsx`,
`pages/teacher/TeacherMessagesPage.tsx`, `features/notifications/kinds.ts`,
`lib/i18n/locales/{vi,en}/{teacher,common}.json`
**Size:** M
**Done when:**
- [ ] The Colleagues tab, and colleague rows merged into All by `lastMessageAt`, as on the F2 page;
      the route `/teacher/messages/colleagues/:colleagueId` opens a thread.
- [ ] A colleague thread polls, pages, sends optimistically, retries and attaches exactly as a
      student's (R7's `useThread` and composer), with no attempt cards and no "Seen by"; a
      disabled colleague replaces the composer with R7's sentence.
- [ ] The bell's `message.received` item with `colleagueId` opens the colleague thread; the
      sidebar count includes colleague threads (it reads `unreadMessages`).
- [ ] Unit tests cover the merge order, the route, the disabled state and the bell target; R7's
      Messages tests pass unedited.

### T-F2.8 — The student's view
**Depends on:** T-F2.0
**Touches (Quizzivy/web):** `web/src/features/messages/pages/student/StudentMessagesPage.tsx`,
`lib/i18n/locales/{vi,en}/student.json`
**Size:** S
**Done when:**
- [ ] A direct row and a thread header with no `classNames` and not `former` read "Teacher at the
      centre" ("Giáo viên của trung tâm"), where R7 wrote "Your teacher" alone; the rest is as at
      v0.15.0. No `/app/*` field is added.
- [ ] A unit test pins the three sub-lines (classes, former, the centre).

## D. Close-out

### T-F2.9 — Seed and E2E
**Depends on:** T-F2.3 to T-F2.8
**Touches:** `Quizzivy/api` `seed/`, `Quizzivy/web` `web/tests/e2e/`
**Size:** M
**Done when:**
- [ ] The seed has a second teacher with a colleague thread with the seeded teacher (a PDF in it)
      and a student in no class.
- [ ] A stubbed E2E walks the picker (filter, search, open an existing thread, start a new one)
      and the Colleagues tab.
- [ ] A live E2E: the seeded Admin writes to a student of the seeded teacher's class, the student
      reads "Giáo viên của trung tâm" and replies; the teacher writes to the student in no class;
      the two teachers exchange a message with a PDF, and the receiver downloads it and sees the
      unread count clear.

### T-F2.10 — Documents
**Depends on:** lands with T-F2.3 to T-F2.8, never after
**Touches (Quizzivy/docs):** `docs/quizzivy-spec-v0.3.md` (§1's Messages line, §8 Messages, §9's
student route row, §13's Messages paragraph and §15's Messages paragraph), `AGENTS.md` (the
non-negotiable on a direct message's two participants), `docs/plan/20-data-model.md`, this file's
"As built" lines
**Size:** S
**Done when:**
- [ ] The spec describes the staff rule, the picker, the centre's teacher on the student's side and
      colleague threads under "Changes pending (F2, v0.15.x)"; the release pull request numbers
      its version.
- [ ] `AGENTS.md`'s rule reads "a direct message is readable by its two participants only, a staff
      member and a student or two staff members".
- [ ] `20-data-model.md` records the colleague columns, the checks and the Down's refusal as a D-row.

### T-F2.11 — Release v0.15.x
**Depends on:** every task above, and v0.15.0 released
**Touches (Quizzivy/docs):** `docs/quizzivy-spec-v0.3.md` (the version line, §18)
**Size:** S
**Done when:** the release checklist below is ticked.

## Order of work

1. T-F2.0 (design) now; the owner answers Q1 to Q13.
2. T-F2.1, cut from sdk `develop` now that R8's contract is there (Quizzivy/sdk#35); it merges after R8's sdk release is cut, green with
   its api pull request.
3. T-F2.2, then T-F2.3, T-F2.4 and T-F2.5 (one lane: the same module and files in places).
4. T-F2.6, T-F2.7 and T-F2.8 once T-F2.0's page is merged; they build against MSW. The locale
   files are serialised.
5. T-F2.9, then T-F2.10 with the code it describes, then the release.

No stack is deeper than two pull requests, and no pull request is opened while another of F2's is
red.

## Release checklist

- [ ] Every task is ticked on `work/messaging-f2`; `develop` (with R8) is merged into it, F2's
      migrations are numbered after R8's, and verification is re-run after that merge;
      `work/messaging-f2` → `develop` (`--no-ff`); `release/0.15.<z>` cut at a named commit.
- [ ] The SDK release sets `info.version`; api and web pin it; `web/package.json` changes in the
      release branch only.
- [ ] Every CI step of 70 §8.1 on the release pull request, judged by exit code, `pnpm e2e:live`
      included.
- [ ] Docs: the release pull request sets the spec's version line and renames "Changes pending
      (F2, v0.15.x)" (spec §18); T-F2.10's "As built" lines are final.
- [ ] The five canaries pass, and their files are as they were at v0.15.0.
- [ ] Security: the isolation suite covers the five new operations and the D17 cases above;
      `permissions.golden` gains exactly the five; the leak review below is in T-F2.1's pull
      request; the `/app/*` leak review lists no field added.
- [ ] Migration: the one file of T-F2.2, rehearsed on a copy of production with timings in the
      release pull request; the deploy is rolling, and a v0.15.0 pod lists, reads and posts as
      before while colleague rows exist.
- [ ] Release note, vi first: any teacher or admin may write to any student; students reply but
      still write first only to their own teachers; colleagues can message each other and share
      files; the "New message" email switch covers colleagues' messages.
- [ ] Verified on production: the owner's account writes to a student of another teacher's class
      and to a student in no class, the student replies, and two staff accounts exchange a file.

### Leak review (for T-F2.1's pull request)

- `listMessageRecipients` (students): id, name, photo, current class names that are not archived.
  Never an email, username, birth date, result, attempt, teacher name or member count. A class
  filter accepts only the caller's classes.
- `listMessageRecipients` (colleagues), `listColleagueThreads`, `getColleagueThread`: a
  colleague's id, name, photo, role name and whether the account is disabled. Never an email
  (narrower than `searchTeacherDirectory`, whose audience is `content.share`), never the
  colleague's other threads, counts or sign-in times.
- `otherClassNames` on `StaffThread` and the peer: names only, never an id, so nothing opens a
  class outside the caller's scope.
- A colleague thread: readable by its two participants only (D17); `scope.all` opens none; an
  Admin naming a colleague reads the Admin's own thread with them.
- The student side: no schema changes, so `/app/*` gains nothing.
- The data export: colleague threads as counts and dates with participant ids, never contents.

## Questions for the owner

Each is drawn at its default on the F2 page; until he answers, the page stands as drawn and the
build reads the default. The same list, in Vietnamese, is on Quizzivy/web#157.

| # | Question | Default |
|---|---|---|
| Q1 | May a student reply in a thread a staff member who does not teach them started? | Yes. R7's code already allows it: a thread that exists is open to both. |
| Q2 | What does the student read for such a staff member? | "Giáo viên của trung tâm" ("Teacher at the centre"), the same for an Admin; no role shown. "Giáo viên cũ" stays for a former teacher. |
| Q3 | Whom may staff start a thread with? | Every enabled student account, in a class or in none. A disabled one is not offered. |
| Q4 | What does a student row show in the picker and the search? | Name, photo and the names of the student's current classes (the caller's first), or "Chưa vào lớp nào". No email or username. |
| Q5 | How do staff find someone to write to? | Both: the list's search finds any student and colleague, and a "Tin nhắn mới" button opens a picker with Students and Colleagues and a class filter. |
| Q6 | Is a class's teacher told when another staff member writes to their student? | No. A thread is private to its two participants (D17). |
| Q7 | Colleague chat: one-to-one only, or groups too? | One-to-one in F2. Groups would be a later release with a members table. |
| Q8 | Who appears as a colleague? | Every enabled account that opens the teacher workspace: teachers, admins and custom staff roles with it. Never a student. |
| Q9 | What does a colleague row show? | Name, photo and role name. No email. |
| Q10 | Which files may colleagues send? | R7's: PDF, Word without macros, PNG, JPEG, MP3, M4A, up to 20 MiB, one per message, both sides. PowerPoint and Excel are not in F2. |
| Q11 | Email for a colleague's message? | Yes, under the same "Tin nhắn mới" switch (in-app and email), with R7's timing; never the body. |
| Q12 | Where do colleague threads sit? | A fourth tab "Đồng nghiệp", and in "Tất cả". |
| Q13 | When does F2 ship? | As v0.15.1, after R8 (v0.15.0). Its contract merges once R8's SDK release is cut. |

## Risks

- **More threads, more email.** Any staff member may now write to any student, and students start
  receiving messages from staff they do not know. The email per thread is still once per 30
  minutes after ten unread minutes; `NOTIFY_EMAIL_EVENTS` can turn `message.received` off.
- **A wider audience for names.** Every holder of `workspace.teacher` can now list every student's
  name and class names, and every colleague's name and role. That is the owner's decision for a
  one-centre organisation; the leak review keeps emails and everything else out.
- **Two contracts in flight.** F2 is planned while R8 is built. The order above (R8's contract,
  R8's sdk release cut, then F2's) and the migration numbering keep them apart; a slip in R8 moves
  F2's build, not R8's.
- **Groups later.** The pair columns fit one-to-one only. If the owner asks for groups (Q7), the
  release that adds them moves colleague threads to a members table, a data migration of rows F2
  creates.
