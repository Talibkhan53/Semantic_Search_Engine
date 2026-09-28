class Display:

    def show_results(self, query, results):

        print(f"\nQuery: {query}")

        print(
            f"{'Rank':<8}"
            f"{'File':<20}"
            f"{'Score':<10}"
        )

        print("-" * 38)

        for rank, result in enumerate(results, 1):

            print(
                f"{rank:<8}"
                f"{result.file_name:<20}"
                f"{result.score:<10.2f}"
            )