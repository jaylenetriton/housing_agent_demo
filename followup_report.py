from housing_tools import get_applications_needing_followup


def main():
    report_date = "2026-10-06"
    applications = get_applications_needing_followup(report_date)

    print(f"Follow-ups due as of {report_date}\n")

    if not applications:
        print("No applications need follow-up.")

    for application in applications:
        print(
            f'{application["application_id"]}: '
            f'{application["first_name"]} {application["last_name"]}'
        )
        print(f'  Email: {application["email"]}')
        print(
            f'  Missing: '
            f'{", ".join(application["missing_requirements"])}'
        )
        print(f'  Submitted: {application["submitted_date"]}')
        print(f'  Previous reminders: {application["reminder_count"]}')
        print(
            f'  Last reminder: '
            f'{application["last_reminder"] or "Never"}'
        )
        print()


if __name__ == "__main__":
    main()