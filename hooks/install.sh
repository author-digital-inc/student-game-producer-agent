#!/bin/sh
# Install the tracking hooks into your GAME repo.
#   sh hooks/install.sh /path/to/your/game/repo
# Run this from the student-game-producer-agent folder.

set -e
GAME_REPO="${1:?usage: sh hooks/install.sh /path/to/your/game/repo}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PRODUCER_DIR="$(cd "$HERE/.." && pwd)"
HOOKS="$GAME_REPO/.git/hooks"

[ -d "$HOOKS" ] || { echo "error: $GAME_REPO has no .git/hooks — is it a git repo?"; exit 1; }

for h in post-commit post-merge; do
  target="$HOOKS/$h"
  if [ -e "$target" ] && ! grep -q "producer-agent" "$target" 2>/dev/null; then
    cp "$target" "$target.pre-producer.bak"
    echo "backed up existing hook -> $target.pre-producer.bak"
  fi
  sed "s#__PRODUCER_DIR__#$PRODUCER_DIR#g" "$HERE/$h" > "$target"
  chmod +x "$target"
  echo "installed $target"
done

echo
echo "done. Test it:  cd \"$GAME_REPO\" && git commit --allow-empty -m 'test hook'"
echo "then check:     ls \"$PRODUCER_DIR/state/\""
