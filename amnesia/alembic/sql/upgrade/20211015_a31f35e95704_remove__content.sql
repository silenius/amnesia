UPDATE permission SET name=split_part(name, '_content', 1);
INSERT INTO role(name, enabled, locked, description) VALUES ('system.Owner', true, true, 'Automatically granted to the creator of an object.');
