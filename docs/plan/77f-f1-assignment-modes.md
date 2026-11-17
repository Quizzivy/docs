# F1 — Assignment modes: strict and flexible (v0.14.x)

A release outside the train, requested by a teacher. An assignment is set up in one of two modes.
**Strict** is the product as it is: the test has a time limit that starts at Start, and the
teacher chooses what happens when a student leaves the paper too often. **Flexible** is new: the
test's deadline is the assignment's close, so a student can stop halfway, take a break and come
back later, on any device, until the close. Integrity events are recorded and the teacher is told,
exactly as under strict, but the teacher configures no action on the attempt: nothing is
auto-submitted, locked or penalised, and the events are information only.

The owner's words (2026-11-17): "bài giao nên được cấu hình 2 loại. Loại một là hiện trạng như bây
giờ - cấu hình thời gian làm bài test nghiêm ngặt. Loại 2 là bài test sẽ có deadline trùng với bài
giao và học sinh có thể nghỉ ngơi trong lúc làm nửa chừng - tuy nhiên vẫn sẽ log lại tất cả các
hành động gian lận của học sinh, vẫn sẽ có thông báo khi học sinh có hành vi gian lận, chỉ khác là
giao viên không cần cấu hình việc gian lận thì làm gì với bài làm đó." He answered the ten
questions below the same day by taking every default ("Theo đề xuất hết"), and placed F1 after
v0.14.0 and before R8 the same way.

It runs like E1 (`74e-e1-group-move.md`): tasks `T-F1.<n>`, branches `feature/t-f1-<nn>-<slug>`
off the integration branch `work/flex-f1`, cut from `develop` once R7 (v0.14.0) is merged there
and released. `work/flex-f1` goes back to `develop` `--no-ff`, then `release/0.14.<z>` → `main` →
back-merge. The number is the first patch free after v0.14.0 and its hotfixes: every change below
is additive, so the SDK gate asks for no new minor (D-080), and `web/package.json` changes only in
the release branch. R7 is not touched and does not grow. R8 (`78-r8.md`) cuts `work/redesign-r8`
after F1 has reached `develop`, or merges `develop` into it before T-R8.1, so the two contract
steps never sit side by side unmerged.

**Deliverable:**

- A **Mode** choice in the assignment wizard and in the Settings tab: Strict (the default) or
  Flexible. Under Flexible the time limit, "Rời khỏi bài" and "Khi vượt giới hạn" are not asked;
  fullscreen and copy-and-paste stay the teacher's switches.
- Under Flexible, every attempt's deadline is its student's close (an override and an early close
  included), and the student is told, on the intro and in the engine, that they may stop and come
  back before it.
- Leaving the paper by the ✕ is a break. The engine records it, the paper is saved, and the
  attempt resumes from Home or the intro on any device. The ✕ leaves fullscreen
  (T-F1.0b, already asked for outside F1).
- Integrity under Flexible: every signal is recorded as today, the first counted absence flags the
  attempt and tells the teacher, later ones tell the teacher again at most every 15 minutes, and
  no absence ever submits or locks the paper.
- The teacher sees two times for every attempt started after F1: **time on the paper** (the
  sittings added up) and **from start to hand-in**. The integrity timeline shows the date where an
  attempt spans more than one day.
- Every existing assignment reads Strict and behaves exactly as before.

**Exit criteria:**

- The five canaries pass untouched.
- No operation is added; the isolation suite and `permissions.golden` do not change.
- `make sdk-check` passes without the `contract-breaking` label.
- A strict assignment behaves exactly as at v0.14.0: its unit, integration and E2E tests pass
  unedited, apart from the ones that pin the two new fields' presence.
- The migration passes goose up/down/up and is rehearsed on a copy of the production database. A
  v0.14.0 pod keeps reading and writing assignments and attempts during the rolling deploy.
- The wizard, the Settings tab, the intro, the engine and the teacher's attempt views match the
  F1 proposal page (T-F1.0) at 360, 768, 1024, 1280 and 1440, in light and dark, with every
  departure a row in `docs/design/gaps.md`.
- Every CI step of `70-redesign-overview.md` §8 is green on the release pull request,
  `pnpm e2e:live` included.

**Depends on:** v0.14.0 released. F1 builds on R3's take-test engine and integrity monitor, R4's
assignment wizard, Settings groups (DG-162), per-student overrides and `schedule.RecomputeDeadlines`,
R4's notifications (`attempt.flagged`), D4's engine rebuild and R5's maintenance windows.

## What exists (develop, 2026-11-17)

Read from `develop` of every repository on 2026-11-17. The names are the code's; line numbers are
left out because they drift.

- **No mode.** `app.assignments.duration_minutes` is `NOT NULL CHECK (1..600)`
  (`00018_create_assignments.sql`), and every attempt's `deadline_at` is
  `min(start + duration, the student's close)` (`attempts/domain/attempt.go`, `Rules.Deadline`).
  Nothing pauses, and nothing measures working time: the teacher's "time" is
  `submittedAt − startedAt` (`web/src/features/assignments/pages/teacher/assignmentDetail.ts`,
  `elapsedMinutes`).
- **Leaving and resuming already work.** The ✕ saves and goes Home (`useLeave.ts`); Home's
  `ResumeCard` and the intro's "Tiếp tục làm bài" call `continueAttempt`; a resume from another
  device issues a new session and writes `resume`, plus `session_takeover` when the old session
  was live in the last two minutes (`attempts/repositories/store.go`, `Resume`). The clock keeps
  running, and the copy says so ("đồng hồ vẫn chạy").
- **Expiry is lazy.** No job sweeps attempts; `ExpireIfDue` closes an overdue one as `timed_out`
  when it is next read (the student, the monitor, the exports). The engine submits
  `timer_expired` at its deadline.
- **Integrity** is per assignment (`IntegrityPolicy`: `requireFullscreen`, `blockCopyPaste`,
  `maxFocusLoss`, `onLimitExceeded` `warn | flag | auto_submit`, `minAwayMs`). Events are
  append-only in `app.attempt_events` with a free-text `kind`. `deriveFocusLoss`
  (`attempts/repositories/autosave.go`) counts away episodes of at least `minAwayMs` and flags only
  when `maxFocusLoss <> 0` and the action is `flag` or `auto_submit`; `closeForFocusLimit`
  (`integrity_submission.go`) auto-submits on save and submit. The integrity settings stay
  editable while the assignment is open and are read on every save.
- **The teacher is told only by the flag.** `attempt.flagged` is written once per attempt, when
  the policy flags it (`support/announcer.go`, dedupe `flagged:<attemptId>`). Under `warn` or an
  unlimited leaving rule nobody is told.
- **Two things assume a short attempt.** A start is refused when `[now, deadline]` meets a
  scheduled maintenance window (`store.go`, `guardStart`, `409 MAINTENANCE_SCHEDULED`), and
  scheduling a window adds its length to every live `deadline_at` past its start
  (`core/maintenance/windows.go`). With a deadline days away, the first would refuse every start
  before any window, and the second would carry an attempt past its close.
- **The lock.** While an assignment is open, changing its version, time limit or attempts answers
  `409 ASSIGNMENT_LOCKED` (`write.go`, `requireUnlocked`; DG-65); the version is also locked once
  any attempt exists.
- **The deck** draws no mode. The teacher deck's New assignment (Time and attempts, Integrity) and
  the student deck's Take test and leave dialog are the surfaces it changes; `docs/design/gaps.md`
  has no row on an untimed or resumable test.

## Decisions taken in this file

- **The mode is a property of the assignment, not of the test.** The same test can be set strict
  for an exam and flexible for homework.
- **The time limit is kept, not dropped, under flexible.** `duration_minutes` stays `NOT NULL`,
  the input still carries `durationMinutes`, and a flexible assignment stores it unapplied, so a
  switch back to strict before the open finds the teacher's value. A nullable column would break
  the v0.14.0 pod's scan during the rolling deploy and a required response field's type.
- **The same for the leaving rule.** `maxFocusLoss` and `onLimitExceeded` stay stored and are not
  applied under flexible. The server decides on the mode, never on those two values, so an old
  tab that sends them cannot turn an action back on.
- **No new notification kind.** A new value of `NotificationKind`, a response enum, is breaking
  (the SDK README). Flexible reuses `attempt.flagged`, whose `focusLost` already carries the
  count, with a second dedupe key per 15-minute bucket for the repeats.
- **A break is the ✕, not a state.** There is no `paused` status: an attempt stays `in_progress`
  until it is handed in or its deadline passes, exactly as today. What changes is the deadline
  and the copy. The ✕ writes a client event `paper_left` (the event log is not an enum), so the
  teacher's timeline can show the break.
- **Time on the paper is reported by the engine and capped by the server.** Derived only from
  events, a sitting that ends with a closed lid has no end. The engine adds up the time the paper
  was visible and sends it with each save; the server never credits more than the time since that
  session's previous report, plus 5 seconds.
- **Maintenance treats a flexible attempt by its close.** A flexible start is refused only while a
  window is under way, and scheduling a window moves a flexible attempt's deadline only by
  recomputing it from its student's close, which the same statement moves when the close falls
  inside the window.
- **The mode locks with the time limit.** Changing it answers `409 ASSIGNMENT_LOCKED` while the
  assignment is open or once any attempt exists: an attempt never changes mode under a student.

## A. Design

### T-F1.0 — Proposal page and the design row
**Depends on:** —
**Touches (Quizzivy/web):** `docs/design/deck/proposals/F1 Assignment Modes.dc.html`,
`docs/design/deck/MANIFEST.sha256`, `docs/design/deck/README.md` (Log), `docs/design/gaps.md`
(DG-232)
**Size:** M
**Done when:**
- [ ] The page follows the proposal layout (cover, decisions, frames at 1280 and 360 in light and
      dark, state table, copy vi/en, open questions, handoff), with the deck's own New
      assignment, Settings, intro and Take test frames set beside the new ones.
- [ ] It draws: the Mode choice in the wizard's Schedule step and what it hides; the Rules step
      under flexible (fullscreen and copy-and-paste only, and one fixed sentence on what is
      recorded and who is told); the Settings tab's mode row and its lock; a mode chip on the
      assignment list and detail; the intro's rules under flexible; the engine's header under
      flexible (the close as a date, a countdown only in the last hour, the danger tone under five
      minutes as today); the leave dialog as a break; the strike dialog under flexible; Home's
      resume card; the monitor's and the attempt sheet's two times; a timeline with dates.
- [ ] DG-232 is added to `gaps.md` and names the page; `node scripts/check-design-deck.mjs` passes
      with the regenerated manifest.
- [ ] A design issue in `Quizzivy/web` with Plan ID DG-232 on the board, and the page published to
      the "Quizzivy mockups" canvas. Questions it leaves go on a "questions for the owner" issue
      for F1.

### T-F1.0b — Fullscreen is left on every way out (outside F1)
Asked by the owner on 2026-11-17, while F1 was being planned, and built on its own from `develop`
(a web change and its spec lines, no contract), so it ships with the first release after it is
merged. Recorded here because the break depends on it: the ✕ and any navigation away from the
paper leave the fullscreen the engine asked for, a submit of any kind already does, Home's
"Tiếp tục làm bài" enters fullscreen again when the paper asks for it, and an intro start that the
server refuses leaves the fullscreen its click entered.

## B. Contract and server

### T-F1.1 — Contract: the mode, time on the paper, the break
**Depends on:** —
**Touches (Quizzivy/sdk):** `api/openapi.yaml`, `sdk/`
**Size:** S
**Done when:**
- [ ] `AssignmentMode` is `strict | flexible`. `Assignment.mode` is required in the response;
      `AssignmentInput.mode` is optional, strict when omitted on create, the stored value when
      omitted on update.
- [ ] `Assignment.durationMinutes` and `IntegrityPolicy.maxFocusLoss` / `onLimitExceeded` say they
      are stored and not applied under flexible; `Assignment`'s deadline rule reads "the student's
      close under flexible".
- [ ] `StudentAssignmentDetail`, `StudentAssignmentCard` and `AttemptSession` carry `mode`.
- [ ] `saveAnswers` and `flushEvents` take an optional `activeMs` (integer, 0 to 600000), the
      paper's visible time since this session's previous report.
- [ ] `MonitorRow` and the teacher's `Attempt` carry `activeSeconds`, nullable: null for an
      attempt started before F1.
- [ ] `UserPreferences.assignmentDefaults` takes an optional `mode`.
- [ ] The event kinds' description names `paper_left`; `attempt.flagged`'s describes the
      flexible repeats. No enum gains a value.
- [ ] `make gen` is its own commit; `make sdk-check` passes without `contract-breaking`.
- [ ] The api pull request on this contract (T-F1.2 onward) is green before this one merges
      (D-082 (iii)).

### T-F1.2 — Migration: the mode and time on the paper
**Depends on:** T-F1.1
**Touches (Quizzivy/api):** `migrations/NNNNN_assignment_mode.sql`,
`server/internal/platform/db/tests/`
**Size:** S
**Done when:**
- [ ] `CREATE TYPE app.assignment_mode AS ENUM ('strict', 'flexible')`;
      `assignments.mode app.assignment_mode NOT NULL DEFAULT 'strict'`. A constant default is
      metadata only on PostgreSQL 18: no rewrite, and the v0.14.0 insert, which names no such
      column, writes strict.
- [ ] `attempts.active_ms bigint NULL CHECK (active_ms >= 0)` and
      `attempts.active_reported_at timestamptz NULL`. Null is "not measured": rows from before F1
      and rows the v0.14.0 pod inserts during the deploy.
- [ ] The down migration drops both columns and the type. goose up/down/up passes, and an
      integration test inserts an assignment and an attempt the v0.14.0 way.
- [ ] `20-data-model.md` gains the section and its D-row (T-F1.10).

### T-F1.3 — Assignments: mode, deadlines, lock, defaults
**Depends on:** T-F1.2
**Touches (Quizzivy/api):** `modules/assignments/{domain,http,repositories}`,
`shared/schedule/deadlines.go`, `modules/attempts/domain/attempt.go`,
`modules/attempts/repositories/store.go`, `core/maintenance/windows.go`, the student read models
(`/app/assignments`, `/app/assignments/{id}`), `modules/identity` preferences
**Size:** M
**Done when:**
- [ ] The mode is read and written with the assignment; a create without it is strict.
- [ ] `Rules.Deadline` under flexible is the student's close (an override's later close and an
      early close included); an override's `durationMinutes` is not applied under flexible.
- [ ] `schedule.RecomputeDeadlines` uses the same rule, so an extension, a reopen or an override
      moves a flexible attempt to its student's new close, and still never earlier.
- [ ] A flexible start is refused only while a maintenance window is under way; scheduling a
      window recomputes flexible attempts from their close instead of adding its length. A strict
      attempt is treated as today. Each is a test.
- [ ] `requireUnlocked` refuses a mode change with `409 ASSIGNMENT_LOCKED` while open or once any
      attempt exists; a change before the open is accepted.
- [ ] The student read models and `AttemptSession` carry `mode`; the `/app/*` leak review lists
      the one field added.
- [ ] `assignmentDefaults.mode` is stored and returned.
- [ ] `extendAttempt` keeps working under flexible: it moves that attempt's deadline past the
      close, as an intervention, and is audited as today.

### T-F1.4 — Integrity and notices under flexible
**Depends on:** T-F1.2
**Touches (Quizzivy/api):** `modules/attempts/repositories/{autosave,events,submit,integrity_submission}.go`,
`modules/attempts/domain/milestones.go`, `modules/attempts/application/internal/support/announcer.go`
**Size:** M
**Done when:**
- [ ] Under flexible, `deriveFocusLoss` flags the attempt at the first counted absence, whatever
      the stored `maxFocusLoss` and `onLimitExceeded`; under strict the SQL is unchanged.
- [ ] Under flexible, `closeForFocusLimit` never closes an attempt, on save or on submit, and a
      client's `auto_submit` reason is rewritten to `manual` as today.
- [ ] The first flag writes `attempt.flagged` with the existing key `flagged:<attemptId>`. Every
      later counted absence under flexible writes it again with the key
      `flagged:<attemptId>:<15-minute bucket>` and the new count, so a teacher is told at most once
      per attempt every 15 minutes. Events that arrive by `flushEvents` are counted and announced
      the same way as those on a save.
- [ ] Strict attempts write exactly what they write at v0.14.0: one notice, at the flag, never
      under `warn`.
- [ ] The recipients are `visibility.PaperReaders`, as today, and the channel follows each
      teacher's preference for `attempt.flagged`, email included where R7 built it.

### T-F1.5 — Time on the paper
**Depends on:** T-F1.2
**Touches (Quizzivy/api):** `modules/attempts/repositories/{autosave,events,store}.go`,
`modules/attempts/http/`, the monitor and attempt read models
**Size:** S
**Done when:**
- [ ] A start sets `active_ms = 0` and `active_reported_at = started_at`; a resume sets
      `active_reported_at` to its time.
- [ ] A save or flush with `activeMs` adds `least(activeMs, now − active_reported_at + 5 s)` to
      `active_ms` and sets `active_reported_at = now`, in the same transaction, only while the
      attempt is in progress and only from its current session; a superseded session's report is
      dropped. A row with a null `active_ms` stays null.
- [ ] `MonitorRow.activeSeconds` and `Attempt.activeSeconds` are `active_ms / 1000`, rounded
      down, or null. Both modes report it.
- [ ] A test pins the cap (a report larger than the time since the last one is cut) and the
      superseded case.

## C. The web

### T-F1.6 — Wizard, Settings, list and defaults
**Depends on:** T-F1.0, T-F1.1
**Touches (Quizzivy/web):** `web/src/features/assignments/{draft,wizardValues,settingsBody,input}.ts`,
`components/wizard/{ScheduleStep,RulesStep}.tsx`, `components/SettingsGroups.tsx`, the assignment
list and detail chips, `features/settings/sections/AssignmentDefaults.tsx`,
`lib/i18n/locales/{vi,en}/teacher.json`
**Size:** M
**Done when:**
- [ ] The Mode choice is drawn as on the F1 page; the draft starts from the teacher's default mode,
      else strict.
- [ ] Under flexible the time limit row and the two leaving controls are not shown, and the body
      still sends the stored `durationMinutes`, `maxFocusLoss` and `onLimitExceeded` unchanged.
- [ ] The Settings tab shows the mode in the Test & timing group and locks it with that group; a
      `409 ASSIGNMENT_LOCKED` on the mode says so in the group's error line.
- [ ] Vietnamese is written first and every new key is listed in the pull request.

### T-F1.7 — The student: intro, engine, leaving and resuming
**Depends on:** T-F1.0, T-F1.1, T-F1.0b
**Touches (Quizzivy/web):** `web/src/features/assignments/{studentRules.ts,pages/AssignmentIntroPage.tsx,components/ResumeCard.tsx}`,
`web/src/features/take-test/{store.ts,useLeave.ts,components/Clock.tsx,components/LeaveDialog.tsx}`,
`web/src/features/integrity/{useIntegrityMonitor.ts,components/StrikeDialog.tsx,strikes.ts}`,
`lib/i18n/locales/{vi,en}/{student,common}.json`
**Size:** M
**Done when:**
- [ ] Under flexible the intro's rules say the student may stop and come back until the close, and
      never that the clock does not stop; strict copy is unchanged.
- [ ] Under flexible the header shows the close as on the F1 page, and the engine submits
      `timer_expired` at that deadline exactly as today.
- [ ] Under flexible the leave dialog is a break ("Tạm nghỉ"), the ✕ records `paper_left` before
      it leaves, and Home's card and the intro resume the attempt.
- [ ] Under flexible the strike dialog says the absence is recorded and the teacher told, with no
      allowance and no submit; `useIntegrityAutoSubmit` never fires.
- [ ] In both modes the engine adds up the paper's visible time, sends it as `activeMs` with each
      save and with the `pagehide` beacon, and saves at least once a minute while the paper is
      visible and time has accrued.
- [ ] Unit tests cover each line above; the engine's existing strict tests pass unedited.

### T-F1.8 — The teacher's attempt views
**Depends on:** T-F1.0, T-F1.1
**Touches (Quizzivy/web):** `web/src/features/attempts/components/{Monitor,AttemptSheet}.tsx`,
`web/src/features/attempts/pages/teacher/AttemptReviewPage.tsx`,
`web/src/features/integrity/{components/Timeline.tsx,timeline.ts}`,
`web/src/features/assignments/pages/teacher/assignmentDetail.ts`,
`web/src/features/notifications/kinds.ts`, `lib/i18n/locales/{vi,en}/{teacher,common}.json`
**Size:** M
**Done when:**
- [ ] The monitor and the attempt sheet show time on the paper and from start to hand-in, as on the
      F1 page; an attempt with `activeSeconds` null shows the second only, as today.
- [ ] The timeline shows the date on the first event of each day once an attempt spans more than
      one, and draws `paper_left` followed by `resume` as a break, in the neutral tone.
- [ ] A repeated `attempt.flagged` reads with its new count; the danger tone and "Flagged" are as
      today.

## D. Close-out

### T-F1.9 — Seed and E2E
**Depends on:** T-F1.3 to T-F1.8
**Touches:** `Quizzivy/api` `seed/`, `Quizzivy/web` `web/tests/e2e/`
**Size:** M
**Done when:**
- [ ] The seed has one flexible assignment open to the seeded student.
- [ ] An E2E walks it: start, answer, take a break by the ✕, resume in a second browser context,
      leave the tab past `minAwayMs` twice, see no submit and no lock, hand in; the teacher sees the
      flag, one notice per 15-minute bucket, the break on the timeline and both times.
- [ ] A live E2E lets a flexible attempt reach its close and finds it `timed_out`.

### T-F1.10 — Documents
**Depends on:** lands with T-F1.3 to T-F1.8, never after
**Touches (Quizzivy/docs):** `docs/quizzivy-spec-v0.3.md` (§9, §10.1 to §10.4, the `Assignment`
and `IntegrityPolicy` types, the notifications rules, the per-student overrides and the
deadline rule), `docs/plan/20-data-model.md`, this file's "As built" lines
**Size:** S
**Done when:**
- [ ] The spec describes both modes where it describes the deadline, leaving, integrity and the
      teacher's notices, and its version is bumped.
- [ ] `20-data-model.md` records `assignment_mode`, `active_ms` and `active_reported_at`.

### T-F1.11 — Release v0.14.x
**Depends on:** every task above
**Size:** S
**Done when:** the release checklist below is ticked.

## Order of work

1. T-F1.0 (design) and T-F1.1 (contract) in parallel. The contract is green and merged first, and
   its `-dev` build is pinned in api and web before anything is built on it.
2. T-F1.2, then T-F1.3, T-F1.4 and T-F1.5 (one lane, the same files in places).
3. T-F1.6, T-F1.7 and T-F1.8 once T-F1.0's page is merged; they build against MSW. The locale
   files are serialised.
4. T-F1.9, then T-F1.10 with the code it describes, then the release.

No stack is deeper than two pull requests, and no pull request is opened while another of F1's is
red.

## Release checklist

- [ ] Every task is ticked on `work/flex-f1`; `develop` is merged into it and verification re-run
      after that merge; `work/flex-f1` → `develop` (`--no-ff`); `release/0.14.<z>` cut at a named
      commit.
- [ ] The SDK release sets `info.version`; api and web pin it; `web/package.json` changes in the
      release branch only.
- [ ] Every CI step of 70 §8.1 on the release pull request, judged by exit code, `pnpm e2e:live`
      included.
- [ ] The five canaries pass, and their files are as they were at v0.14.0.
- [ ] Security: no operation added; `permissions.golden` unchanged; the `/app/*` leak review lists
      `mode` as the only student field added.
- [ ] Migration: the one file of T-F1.2, rehearsed on a copy of production; the deploy is rolling,
      and a v0.14.0 pod reads strict for every row.
- [ ] Verified on production: an existing assignment reads strict and its attempts are unchanged;
      a flexible assignment made by the owner's account starts, takes a break, resumes and hands in.

## Decided

The owner, 2026-11-17, answering in Vietnamese with "Theo đề xuất hết": every default below, and
F1's place as its own release after v0.14.0 and before R8.

| # | Question | Decided |
|---|---|---|
| Q1 | Does flexible keep a per-attempt time limit? | No. The deadline is the student's close; per-student overrides of the close still apply. |
| Q2 | What happens to an attempt still in progress at the close? | It is submitted automatically, as today, and reads "timed out". The day-before and hour-before reminders stay. |
| Q3 | Can a student resume on another device? | Yes, as today. The new tab or device takes the paper over, the old one locks, and the teacher's timeline reads "Resumed in another tab or device". |
| Q4 | Does a break count as leaving the paper? | No. A break is the ✕ (answers saved) or closing the page. An absence is counted only while the paper is open and the student switches tab or application. |
| Q5 | When is the teacher told? | At the first counted absence (3 s or more by default), which also flags the attempt; later ones together, at most one notice per attempt every 15 minutes. No action on the attempt. |
| Q6 | Fullscreen and copy-and-paste under flexible? | The teacher's switches, as today. Only "Rời khỏi bài" and "Khi vượt giới hạn" go. |
| Q7 | How is time shown to the teacher? | Two times: on the paper (the sittings added up) and from start to hand-in. The timeline gains dates. |
| Q8 | Attempts under flexible? | As today: 1 to 99, the best counts, and each attempt runs to the close. |
| Q9 | Existing assignments? | All strict. A new assignment is strict unless the teacher's stored default says flexible. |
| Q10 | Can the mode change after students start? | No. It locks with Test & timing while open and once any attempt exists; before the open it can change. |

## Risks

- **A long attempt meets every release.** A flexible attempt is open across deploys. A deploy
  restarts the API for seconds and the engine retries saves; a new build under an open tab is
  handled by `src/app/boot/version.ts`. Nothing new, but over days it is certain rather than rare.
- **Lazy expiry over days.** A flexible attempt nobody opens after its close stays `in_progress`
  in the table until a read expires it, as a strict one does today; the monitor, the exports and
  the retention sweep (which never touches one in progress) already read through that.
- **Notices.** The 15-minute bucket bounds the in-app list. With R7's email channel on for
  `attempt.flagged`, a student who leaves often sends a teacher up to four emails an hour for one
  attempt; the teacher's switch is the remedy, and the release note says so.
- **Client-reported time.** `activeMs` is the browser's word, capped by the server's clock, so it
  can under-report (a lost beacon) but never exceed the time that passed. The teacher's view calls
  it time on the paper, not proof of work.
