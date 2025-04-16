import multiprocessing

import optuna


def objective(trial):
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2


def run_study():
    study = optuna.load_study(
        study_name="my_parallel_study",
        storage="sqlite:///example.db"
    )
    study.optimize(objective, n_trials=4)


if __name__ == "__main__":
    study = optuna.create_study(
        study_name="my_parallel_study",
        storage="sqlite:///example.db",
        direction="minimize",
        load_if_exists=True
    )

    # Starte mehrere Worker
    processes = []
    for _ in range(2):  # z. B. 4 parallele Worker
        p = multiprocessing.Process(target=run_study)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print()
