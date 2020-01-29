#!/usr/bin/env bash

cleanup() {
    rv=$?
    # on exit code 1 this is normal (some tests failed), do not stop the build
    if [ "$rv" = "1" ]; then
        exit 0
    else
        exit $rv
    fi
}

trap "cleanup" INT TERM EXIT

#if hash pytest 2>/dev/null; then
#    echo "pytest found"
#else
#    echo "pytest not found. Trying py.test"
#fi

# First the raw for coverage
echo -e "\n\n****** Running tests ******\n\n"
if [ "${TRAVIS_PYTHON_VERSION}" = "3.5" ]; then
   # copy the conftest.py file before executing.
   # cp ci_tools/conftest.py vtypes/
   # Note: an alternative could be to add ci_tools/ at the end of the below command but not sure it will be applied on all tests.

   coverage run --source vtypes -m pytest --junitxml=reports/junit/junit.xml --html=reports/junit/report.html -v vtypes/
   # python -m pytest --junitxml=reports/junit/junit.xml --html=reports/junit/report.html --cov-report term-missing --cov=./vtypes -v vtypes/
else
   # faster - skip coverage and html report
   python -m pytest --junitxml=reports/junit/junit.xml -v vtypes/
fi
