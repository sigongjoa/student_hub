#let data = json(sys.inputs.data_file)

#set page(paper: "a4", margin: 2cm)
#set text(font: ("NanumGothic", "Arial"), size: 10pt)

#align(center, text(17pt, weight: "bold")[[Node 0] Student Hub Test Report])
#v(1cm)

= 1. Test Overview
- *Run Date*: #data.run_date
- *Status*: #text(fill: green, weight: "bold")[SUCCESS]

= 2. Created Student
#table(
  columns: (auto, 1fr),
  inset: 10pt,
  align: horizon,
  [*ID*], [#data.student.id],
  [*Name*], [#data.student.name],
  [*Grade*], [#str(data.student.grade)],
  [*School*], [#data.student.school_code],
)

= 3. Unified Profile (Aggregated)
This section verifies that Node 0 successfully aggregated data from multiple sources (mocked).

== Mastery Summary (Node 2 Mock)
- *Average Mastery*: #data.profile.mastery_summary.average
- *Total Attempts*: #data.profile.mastery_summary.total_attempts
- *Recent Trend*: #data.profile.mastery_summary.recent_trend

== Heatmap Data (Node 4 Mock)
#table(
  columns: (1fr, 1fr),
  inset: 5pt,
  fill: (_, row) => if calc.odd(row) { luma(240) } else { none },
  [*Concept*], [*Mastery*],
  ..data.profile.heatmap_data.pairs().map(((k, v)) => ([#k], [#v])).flatten()
)

== Recent Activities
#for activity in data.profile.recent_activities [
  - #activity.date: *#upper(activity.type)* - Score: #activity.score
]

= 4. Generated Intervention
Automatic intervention generated based on the test scenario.

- *Trigger*: #data.intervention.trigger
- *Type*: #data.intervention.intervention_type
- *Reason*: #data.intervention.reason

== Executed Actions
#for action in data.intervention.actions [
  #block(stroke: gray, inset: 10pt, radius: 5pt)[
    *Type*: #action.action_type \
    *Status*: #action.status \
    *Params*: #str(action.params)
  ]
  #v(5pt)
]

#v(2cm)
#align(center)[*End of Report*]
