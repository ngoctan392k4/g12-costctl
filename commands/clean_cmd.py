"""clean — (stretch) bulk terminate resources matching a tag.

WARNING — DESIGN-FOR-SAFETY
---------------------------
This is the most dangerous command in the CLI. Get the contract right:

  1. DEFAULT IS DRY-RUN. Without --apply the command MUST NOT touch resources.
     It only lists what WOULD be deleted.
  2. Even with --apply, you should consider printing a summary count first
     ("about to terminate N EC2 + M volumes — proceed?"), though for this
     starter a hard `--apply` flag is enough.
  3. Never use this with a tag you don't fully own. Reflection prompt in
     README covers the blast-radius scenario.

WHAT YOU MUST BUILD
-------------------
1. `_find_targets(tag_key, tag_val)` — return a dict like:
     {"ec2": [<instance ids in non-terminal state>],
      "volume": [<volume ids in 'available' state only>]}
   Skip terminated/shutting-down instances (already gone).
   Skip in-use volumes (can't delete while attached — would error anyway).

2. `run(args)` — call _find_targets, print the plan, then either:
     - bail with "(dry-run — pass --apply to ...)"  (default)
     - or actually terminate (when --apply)

HELPERS YOU CAN USE
-------------------
From commands._common:
  parse_kv(s) -> (k, v)

AWS APIS YOU'LL NEED
--------------------
- ec2.describe_instances() + describe_volumes() — same as list_cmd
- ec2.terminate_instances(InstanceIds=[...])
- ec2.delete_volume(VolumeId=...)  (per volume, no bulk API)

VERIFY
------
    pytest tests/test_clean.py -v
"""
import boto3

from commands._common import parse_kv, tags_to_dict


def _find_targets(tag_key, tag_val):
    """Return {"ec2": [...], "volume": [...]} matching tag in non-terminal state."""
    ec2 = boto3.client("ec2", region_name="us-east-1")

    targets = {
        "ec2": [],
        "volume": [],
    }

    # Find EC2 instances matching tag
    resp = ec2.describe_instances()

    for reservation in resp.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            tags = tags_to_dict(instance.get("Tags", []))

            if tags.get(tag_key) == tag_val:
                state = instance.get("State", {}).get("Name")

                # Skip already-gone instances
                if state not in ("terminated", "shutting-down"):
                    targets["ec2"].append(instance["InstanceId"])

    # Find EBS volumes matching tag
    vol_resp = ec2.describe_volumes()

    for volume in vol_resp.get("Volumes", []):
        tags = tags_to_dict(volume.get("Tags", []))

        if tags.get(tag_key) == tag_val:
            # Only delete detached / available volumes
            if volume.get("State") == "available":
                targets["volume"].append(volume["VolumeId"])

    return targets
    # raise NotImplementedError("TODO: implement _find_targets — see test_clean.py")


def run(args):
    """Entry point.

    Args set by argparse:
        args.tag    — "key=value" string (REQUIRED)
        args.apply  — bool, must be True to actually delete (default False = dry-run)
    """
    key, value = parse_kv(args.tag)
    targets = _find_targets(key, value)

    total = sum(len(ids) for ids in targets.values())

    if total == 0:
        print("Nothing to clean")
        return

    # Default: dry-run only
    if not args.apply:
        print(f"dry-run: found {total} resource(s) for {key}={value}")

        for iid in targets["ec2"]:
            print(f"Would terminate EC2 {iid}")

        for vid in targets["volume"]:
            print(f"Would delete volume {vid}")

        print("dry-run — pass --apply to actually clean resources")
        return

    # Apply mode: actually terminate/delete
    ec2 = boto3.client("ec2", region_name="us-east-1")

    for iid in targets["ec2"]:
        ec2.terminate_instances(InstanceIds=[iid])
        print(f"Terminated EC2 {iid}")

    for vid in targets["volume"]:
        ec2.delete_volume(VolumeId=vid)
        print(f"Deleted volume {vid}")
    # raise NotImplementedError("TODO: implement run() — see module docstring")
