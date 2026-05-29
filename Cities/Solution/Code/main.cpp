#include <algorithm>
#include <iostream>
#include <limits>
#include <queue>
#include <stack>
#include <tuple>
#include <utility>
#include <vector>

struct Edge {
    int to;
    int len;
};

struct Candidate {
    int len;
    int city;
    int from;
};

struct CandidateCmp {
    bool operator()(const Candidate& a, const Candidate& b) const {
        if (a.len != b.len) {
            return a.len > b.len;
        }
        if (a.city != b.city) {
            return a.city > b.city;
        }
        return a.from > b.from;
    }
};

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n = 0;
    int m = 0;
    if (!(std::cin >> n >> m)) {
        std::cerr << "Ошибка: не удалось прочитать n и m.\n";
        return 1;
    }

    if (n <= 0 || m < 0) {
        std::cerr << "Ошибка: некорректные значения n или m.\n";
        return 1;
    }

    std::vector<std::vector<Edge>> graph(n + 1);
    for (int e = 0; e < m; ++e) {
        int u = 0;
        int v = 0;
        int len = 0;
        if (!(std::cin >> u >> v >> len)) {
            std::cerr << "Ошибка: не удалось прочитать дорогу на строке " << (e + 1) << ".\n";
            return 1;
        }

        if (u < 1 || u > n || v < 1 || v > n || len < 0) {
            std::cerr << "Ошибка: некорректные данные дороги на строке " << (e + 1) << ".\n";
            return 1;
        }

        graph[u].push_back({v, len});
        graph[v].push_back({u, len});
    }

    int k = 0;
    if (!(std::cin >> k)) {
        std::cerr << "Ошибка: не удалось прочитать число столиц k.\n";
        return 1;
    }
    if (k <= 0 || k > n) {
        std::cerr << "Ошибка: некорректное число столиц k.\n";
        return 1;
    }

    {
        std::vector<char> used(n + 1, 0);
        std::stack<int> st;
        st.push(1);
        used[1] = 1;

        while (!st.empty()) {
            const int v = st.top();
            st.pop();
            for (const auto& edge : graph[v]) {
                if (!used[edge.to]) {
                    used[edge.to] = 1;
                    st.push(edge.to);
                }
            }
        }

        for (int v = 1; v <= n; ++v) {
            if (!used[v]) {
                std::cerr << "Ошибка: граф дорог несвязный, корректное распределение невозможно.\n";
                return 1;
            }
        }
    }

    std::vector<int> capitals(k + 1, 0);
    std::vector<int> owner(n + 1, 0);
    std::vector<std::vector<int>> states(k + 1);

    for (int state = 1; state <= k; ++state) {
        int cap = 0;
        if (!(std::cin >> cap)) {
            std::cerr << "Ошибка: не удалось прочитать столицу для государства " << state << ".\n";
            return 1;
        }
        if (cap < 1 || cap > n) {
            std::cerr << "Ошибка: некорректный номер столицы.\n";
            return 1;
        }
        if (owner[cap] != 0) {
            std::cerr << "Ошибка: столица " << cap << " указана более одного раза.\n";
            return 1;
        }

        capitals[state] = cap;
        owner[cap] = state;
        states[state].push_back(cap);
    }

    int assigned = k;

    std::vector<std::priority_queue<Candidate, std::vector<Candidate>, CandidateCmp>> frontiers(k + 1);

    auto push_edges = [&](int state, int city) {
        for (const auto& edge : graph[city]) {
            if (owner[edge.to] == 0) {
                frontiers[state].push({edge.len, edge.to, city});
            }
        }
    };

    for (int state = 1; state <= k; ++state) {
        push_edges(state, capitals[state]);
    }

    while (assigned < n) {
        bool progress = false;

        for (int state = 1; state <= k && assigned < n; ++state) {
            auto& pq = frontiers[state];
            while (!pq.empty() && owner[pq.top().city] != 0) {
                pq.pop();
            }
            if (pq.empty()) {
                continue;
            }

            const Candidate best = pq.top();
            pq.pop();

            owner[best.city] = state;
            states[state].push_back(best.city);
            ++assigned;
            progress = true;

            push_edges(state, best.city);
        }

        // Для связного графа и корректного входа сюда не попадем,
        // но защита помогает избежать зацикливания на плохих данных.
        if (!progress) {
            std::cerr << "Ошибка: не удалось распределить все города, присвоено только " << assigned
                      << " из " << n << ".\n";
            return 1;
        }
    }

    for (int state = 1; state <= k; ++state) {
        std::cout << "Государство " << state << ":";
        for (int city : states[state]) {
            std::cout << ' ' << city;
        }
        std::cout << '\n';
    }

    return 0;
}
