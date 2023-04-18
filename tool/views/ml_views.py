import os

import torch
from torch import nn

from django.http import JsonResponse

HEROES_IN_DOTA = 123

device = torch.device("cpu")  # cpu, gpu, mps


class DotaModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.fc = nn.Sequential(
            nn.Linear(10 * HEROES_IN_DOTA, 64),
            nn.ReLU(),
            nn.Linear(64, 10),
            nn.ReLU(),
            nn.Linear(10, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.fc(x)


def get_dota_prediction(starting_team_picks, second_team_picks):
    picks = [0] * 10 * HEROES_IN_DOTA
    for i in range(5):
        picks[i * HEROES_IN_DOTA + starting_team_picks[i]] = 1

    for i in range(5, 10):
        picks[i * HEROES_IN_DOTA + second_team_picks[i - 5]] = 1

    picks = torch.as_tensor(picks).float().to(device)

    pwd = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(pwd, "../ml_models/DotaModel_t20_14_34_v2_l0.323_a0.876.pt")

    model = DotaModel().to(device)
    model.load_state_dict(torch.load(path, map_location=device))

    model.eval()
    with torch.no_grad():
        outputs = model(picks)

    starting_team_win_probability = round(100 * outputs.item(), 1)

    return starting_team_win_probability


def ml_dota_prediction(request):
    """Predict Dota match result by draft."""
    params = request.GET.copy()
    team1 = [int(x) for x in params.get("team1").split(",")]
    team2 = [int(x) for x in params.get("team2").split(",")]

    return JsonResponse(get_dota_prediction(team1, team2), safe=False)
