

### Findability

I define the findability of a document $d$ under a system $M$ as:

$$
F_{M}(d)
    = \sum_{q} g(d, q) P_d(q)
    = \mathbb{E}_{q \sim P_d(q)} g(d, q)
$$

where:

* $g(d, q)$ measures how much $d$ is relevant to $q$ according to $M$ e.g. $g(d, q) = 1 / p_{dq}$, where $p_{dq}$ is the rank of $d$ for $q$.
* $P_d(q)$ is the probability distribution of queries $q$ for which $d$ is relevant, i.e. $P_d(q) = P(q \mid d, r=1)$, where $P$ is the "ground truth" distribution.

In practice we can estimate $F_M(d)$ by computing the average of $g(d, q)$ over a set of queries $Q_d$ for which $d$ is relevant, i.e. $\hat{F}_M(d) = \frac{1}{|Q_d|} \sum_{q \in Q_d} g(d, q)$.


### Prior relevance

$P_{M}(q, d, r)$ is the joint probability distribution of queries $q$, documents $d$, and relevance $r$ that generates the training data for a system $M$. 

Let's define the "prior relevance" or "global relevance" of a document $d$ for distribution $P_{M}$ as:

$$
\rho_{M}(d) 
    = P_{M}(r=1 \mid d)
    = \sum_{q} P_{M}(r=1 \mid d, q) P_{M}(q \mid d)
    = \mathbb{E}_{q \sim P_{M}(q \mid d)} P_{M}(r=1 \mid d, q)
$$

where:

* $P_{M}(r=1 \mid d, q)$ is the probability that $d$ is relevant to $q$ in M's training data generation process.
* $P_{M}(q \mid d)$ is the conditional probability distribution of queries $q$ given $d$ in the training data.

Let's assume that $M$ is able to perfectly learn $P_{M}(r=1 | q, d)$ from data, i.e. the probability that $d$ is relevant to $q$ in the data generating process. 

Let's also assume that we can perfectly learn $P_{M}(r=1 \mid d)$ by training a binary relevance model on the training data, disregarding query information. 


### Ideas

**Low prior relevance $\rho_{M}(d)$ can "lead to" low posterior relevance $P_{M}(r=1 \mid d, q)$**


We express the "posterior" relevance of $d$ given $q$ as a function of the "prior" relevance of $d$:

$$
P_{M}(r=1 \mid d, q) 
    = \frac{P_{M}(r=1 \mid d) P_{M}(q \mid d, r=1)}{P_{M}(q \mid d)}
$$

and by total probability:

$$
P_{M}(q \mid d) 
    = P_{M}(q \mid d, r=1) P_{M}(r=1 \mid d) + P_{M}(q \mid d, r=0) P_{M}(r=0 \mid d)
$$

That is:

$$
P_{M}(r=1 \mid d, q) 
    = f(\rho_{M})
    = \frac{a \cdot \rho_{M}(d)}{a \cdot \rho_{M}(d) + b \cdot (1 - \rho_{M}(d))}
$$

with $a = P_{M}(q \mid d, r=1)$ and $b = P_{M}(q \mid d, r=0)$.

We see that:

$$
\frac{df}{d\rho_{M}} 
    = \frac{a}{(a \cdot \rho_{M} + b \cdot (1 - \rho_{M}))^2}
    > 0
$$

The posterior relevance $P_{M}(r=1 \mid d, q)$ is a monotonically increasing function of the prior relevance $\rho_{M}(d)$, for fixed $a$ and $b$.


**Low prior relevance $\rho_{M}(d)$ can "lead to" low findability $F_{M}(d)$**


Let's assume that we set $g(d, q) = P_{M}(r=1 \mid d, q)$, the probability learned by $M$. Then we can rewrite the findability of $d$ as:

$$
F_{M}(d)
    = \sum_{q} P_{M}(r=1 \mid d, q) P(q \mid d, r=1)
    = \mathbb{E}_{q \sim P(q \mid d, r=1)} P_{M}(r=1 \mid d, q)
$$

Because $P_{M}(r=1 \mid d, q)$ is monotonically increasing in $\rho_{M}(d)$ for every $q$, the expectation over any distribution of $q$ will also be monotonically increasing in $\rho_{M}(d)$.

Therefore $F_{M}(d)$ is also monotonically increasing in $\rho_{M}(d)$, for fixed $P(q \mid d, r=1)$.



**"Biased" training data affects the findability of documents**

We assume a "biased" training distribution $P_{M}(q, d, r) \neq P(q, d, r)$, such that:

$$
\rho_{M}(d) < \rho(d)
$$

for some group of documents $d \in D$. That is, for this documents the prior relevance $\rho_{M}(d)$ is lower than the "ground truth" prior relevance $\rho(d)$.

We know from before that $\rho_{M}(d) < \rho(d)$ leads to $P_{M}(r=1 \mid d, q) < P(r=1 \mid d, q)$ for any $q$, and thus to $F_{M}(d) < F(d)$.

----



### ETC



Feeling that I am reinventing the wheel.


**For an unsupervised retriever:**

We can assume constant prior relevance $\rho_{M}(d)$ for all documents. Then we can express the posterior:

$$
P_{M}(r=1 \mid d, q) 
    = \frac{P_{M}(q \mid d, r=1)}{P_{M}(q \mid d)} \cdot \text{const}
    \propto \frac{P_{M}(q \mid d, r=1)}{P_{M}(q \mid d)}
$$



------




Assume we have different documents, all _actually_ relevant to their own set of queries:

$$
d_i \text{ relevant to } q \in Q_{d_i}
$$


* Under which conditions can we expect $F_{M}(d)$ to be correlated with $\rho_{M}(d)$?
* Under which conditions can we expect $F_{M}(d)$ to be the same for any value of $\rho_{M}(d)$?



-----------------


Two documents $d_1, d_2$ with equal "ground truth" relevance $P(r=1 \mid d, q)$ to some query $q$ can have different $P_{M}(r=1 \mid d_i, q)$, e.g., because of labeling bias in the training data.


