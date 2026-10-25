# relay/

Patches the hub cannot push itself, left here for the session that can. Each file is
`git format-patch` output; apply with `curl -sL <raw url> | git am`. The receiving session
deletes the file (or the hub does) once the commit is on its branch.
