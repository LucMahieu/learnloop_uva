import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.ticker import MaxNLocator

def extract_question_dates(user_log, after_date):
    dates = []
    for segment_value in user_log.values():
        if segment_value["type"] == "question":
            entry_dates = [entry_date for entry_date in segment_value['entries'] if entry_date > after_date]
            if entry_dates != []:
                dates.append(entry_dates[0]) # Only include the first date bc we want to count the unique questions

    return dates

def calculate_percentage(questions_made, total_questions):
    percentage = (len(questions_made) / total_questions) * 100
    return percentage

def cluster_percentages(percentages):
    clusters = defaultdict(int)
    for percent in percentages:
        if 0 <= percent <= 10:
            clusters["0%-10%"] += 1
        elif 11 <= percent <= 20:
            clusters["11%-20%"] += 1
        elif 21 <= percent <= 30:
            clusters["21%-30%"] += 1
        elif 31 <= percent <= 40:
            clusters["31%-40%"] += 1
        elif 41 <= percent <= 50:
            clusters["41%-50%"] += 1
        elif 51 <= percent <= 60:
            clusters["51%-60%"] += 1
        elif 61 <= percent <= 70:
            clusters["61%-70%"] += 1
        elif 71 <= percent <= 80:
            clusters["71%-80%"] += 1
        elif 81 <= percent <= 90:
            clusters["81%-90%"] += 1
        elif 91 <= percent <= 100:
            clusters["91%-100%"] += 1
    return clusters

def plot_clusters(clusters):
    sorted_clusters = dict(sorted(clusters.items(), key=lambda x: int(x[0].split('%')[0].split('-')[0])))
    categories = list(sorted_clusters.keys())
    counts = list(sorted_clusters.values())
    
    plt.bar(categories, counts, edgecolor='blue')
    plt.xlabel('Percentage gemaakte vragen')
    plt.ylabel('Aantal studenten')
    plt.title('Cluster percentage gemaakte vragen')
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.show()


def count_all_questions(all_data):
    total = 0
    for value in all_data[0].values():
        if value["type"] == "question":
            total += 1
    return total


if __name__ == "__main__":
    all_data = [
                {
    "0": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "1": {"type": "theory", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "2": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "3": {"type": "question", "entries": []},
    "4": {"type": "question", "entries": []},
    "5": {"type": "question", "entries": []},
    "6": {"type": "question", "entries": []},
    
    },
                {
    "0": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "1": {"type": "theory", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "2": {"type": "question", "entries": []},
    "3": {"type": "question", "entries": []},
    "4": {"type": "question", "entries": []},
    "5": {"type": "question", "entries": []},
    "6": {"type": "question", "entries": []},
    
    },
        {
    "0": {"type": "question", "entries": []},     
    "1": {"type": "theory", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "2": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "3": {"type": "question", "entries": []},
    "4": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "5": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "6": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    },
            {
    "0": {"type": "question", "entries": []},     
    "1": {"type": "theory", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "2": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "3": {"type": "question", "entries": []},
    "4": {"type": "question", "entries": []},
    "5": {"type": "question", "entries": []},
    "6": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    },
                {
    "0": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},     
    "1": {"type": "theory", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "2": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "3": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "4": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "5": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    "6": {"type": "question", "entries": ["2024-05-01", "2024-05-04", "2024-05-06"]},
    }
    ]

    all_percentages = []

    numb_of_questions = count_all_questions(all_data)
    print(numb_of_questions)

    for individual_data in all_data:
        # Extract question dates
        individual_question_dates = extract_question_dates(individual_data, "2024-01-30")
        print(f"individual_question_dates: {individual_question_dates}")
        individual_percentage = calculate_percentage(individual_question_dates, numb_of_questions)
        print(individual_percentage)
        
        all_percentages.append(individual_percentage)
        print(all_percentages)

    clusters = cluster_percentages(all_percentages)
    plot_clusters(clusters)