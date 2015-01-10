
fab -u root -p harry4u hosts:beta,api,Y upstart:start
fab -u root -p harry4u hosts:beta,worker,Y upstart:start
fab -u root -p harry4u hosts:beta,singleton,Y upstart:start
