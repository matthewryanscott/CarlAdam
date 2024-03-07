.POSIX:

test:
	poetry run pytest \
		--cov=carladam.petrinet --cov=carladam.util --cov-fail-under=100 \
		--doctest-modules --doctest-glob="*.md" \
		carladam/petrinet \
		carladam/util \
		tests

simulator:
	poetry run python -m carladam.django.simulator examples
