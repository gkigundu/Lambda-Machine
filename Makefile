pull:
	git pull
push:
	git push --repo=git@github.com:XDerekMaierX/Lambda-Machine.git -q
	if test "$$(git status -s | wc -l)" -eq 0; then echo "<log> Push: Up to date"; else make updateGit; fi
viewChanges:
	git log -p
updateGit:
	git add .
	git commit
	git push --repo=git@github.com:XDerekMaierX/BashTools.git

