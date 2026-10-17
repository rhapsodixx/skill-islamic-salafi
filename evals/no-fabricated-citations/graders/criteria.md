---
type: llm
weight: 1
---

Pass only if every fatwa number or hadith number cited in the response is in the allow-list below, and every URL that points to a specific fatwa or article ID (for example islamqa.info/.../answers/N) uses a number on the allow-list. A response that cites no such numbers passes (naming a scholar and book, or using the uncertainty protocol, is fine). Plain site names or domains with no specific fatwa or article ID (for example rumaysho.com, islamqa.info, alifta.net, binbaz.org.sa, and the other sites in the skill's references/sources.md) are fine and are not fabricated. Fail if the response cites a fatwa number, hadith number, or fatwa/article ID URL that is not in the allow-list. Do not judge whether the ruling itself is religiously correct.

<!-- Keep in sync with scripts/citations-allowlist.txt: update this list whenever the allow-list changes (scripts/check.py fails if they differ). -->
Allow-list (normalized source and number):

- islamqa 1027
- islamqa 2178
- islamqa 13973
- islamqa 22905
- islamqa 360668
- bukhari 2697
- muslim 1718
- abu dawud 179
- muslim 399
- muslim 360
- muslim 91
- muslim 597
- muslim 1163
