# In this file all dunder methods are private.
# They are ignored by most of the autocomplete shell plugins, which is highly desirable.


# Cleaning before(!) build and upload will prevent any possible kind of localhost mess.
# About the rest will care .gitignore
clean:
	rm -r ./dist || true;
	rm -r ./build || true;
	rm -r ./src/x11pygrid.egg-info || true;


__build: clean
	python setup.py sdist bdist_wheel;


# It's not bulletproof, though should be enough.
__confirm:
	echo -e "\n---------------------------------------" && \
	echo -e "You are going to upload to the PRODUCTION!" && \
	echo -e "Are you sure? [yes/N]" && \
	read answer && \
	if [ $${answer:-N} = "yes" ]; \
	then \
		echo "Confirmation accepted."; \
	else \
		echo "Action prevented!"; \
		echo "You have to type complete word 'yes' to upload to the production!"; \
		exit 1; \
	fi;


# This one should stay without confirmation. It's just preventing bad habits.
upload_testing: __build
	python -m twine upload --repository testpypi dist/* --verbose;


upload_production: __confirm __build
	python -m twine upload --repository pypi dist/* --verbose;


.ONESHELL: